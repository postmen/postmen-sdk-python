"""Postmen and PostmenException classes are intended for SDK users.
"""

import sys
import json
import time as time_module
import datetime
import traceback
import threading

import six
import requests

from .jsont import JSONWithDatetimeEncoder
from .jsont import JSONWithDatetimeDecoder
if six.PY2:
    from .rp2 import _raise
else:
    from .rp3 import _raise

__author__ = 'Postmen <support@postmen.com>'

class PostmenException(Exception):
    """Include errors reported by API, related to API (e.g. rate limit) and other exceptions during API calls (e.g. HTTP connectivity issue)."""
    def __init__(self, message=None, **kwarg):
        self.a = kwarg
        if 'meta' not in self.a:
            self.a['meta'] = {}
        if 'data' not in self.a:
            self.a['data'] = None
        if message:
            self.a['meta']['message'] = message
        code = kwarg.get('code', None)
        self._setDefault('code', code)
        self._setDefault('details', [])
        self._setDefault('retryable', False)
        self._setDefault('message', 'no details')


    def __str__(self):
        msg = self.message()+((' (%s)' % str(self.code())) if self.code() else "")
        return msg

    def _setDefault(self, key, default_value):
        if key not in self.a['meta']:
            self.a['meta'][key] = default_value

    def traceback(self):
        """:returns: error's traceback object. Traceback must be passed explicitly thru constructor method
        :rtype: traceback object"""
        return self.a['meta']['traceback']

    def code(self):
        """:returns: API error code
        :rtype: int or None"""
        return self.a['meta']['code']

    def message(self):
        """:returns: API error human readable message
        :rtype: str or unicode"""
        return self.a['meta']['message']

    def details(self):
        """:returns: API error details
        :rtype: list"""
        return self.a['meta']['details']

    def retryable(self):
        """:returns: indicate if API call is retryable
        :rtype: bool"""
        return self.a['meta']['retryable']

    def data(self):
        """:returns: API call data (if any)
        :rtype: dict"""
        return self.a['data']

class Postmen(object):
    """Postmen calls handler.

    :param api_key: Postmen API key
    :type api_key: str or unicode
    :param region: avalible regions: sandbox, us-west, ap-southeast. Part of API endpoint
    :type region: str or unicode
    :param endpoint: raw API endpoint string, overwrite region setting
    :type endpoint: str or unicode
    :param version: API version, use to create endpoint
    :type version: str or unicode
    :param x_agent: HTTP header x-postmen-agent tag value
    :type x_agent: str or unicode
    :param retries: number of calls retries in case of retriable errors
    :type retries: int
    :param raw: True to exclude parsing of response JSON strings
    :type raw: bool
    :param safe: True to suppress exceptions on API calls (only). Use getError() instead
    :type safe: bool
    :param time: True to convert ISO time strings to datetime.datetime
    :type time: bool
    :param proxy: Proxy for HTTP calls
    :type proxy: dictionary like in http://docs.python-requests.org/en/latest/user/advanced/#proxies
    :param retry: True to retry calls in case of retriable errors
    :type retry: bool
    
    :raises PostmenException: if API is missed
    :raises PostmenException: if region or endpoint is missed
    :raises PostmenException: if version is missed
    """
    def __init__(
        self, api_key, region=None, endpoint=None,
        raw=False, safe=False, time=False, proxy={}, retry=True, rate = True
    ):
        e = None
        if not api_key:
            e = PostmenException(message='missed API key')
        if not region and not endpoint:
            e = PostmenException(message='missed region')
        self._retries = 5
        self._error = None
        self._version = 'v3'
        self._calls_left = None
        self._time_before_reset = None
        self._endpoint = endpoint if endpoint else 'https://%s-api.postmen.com' % region
        self._headers = {'content-type': 'application/json'}
        self._headers['postmen-api-key'] = api_key
        self._headers['x-postmen-agent'] = 'python-sdk-1.0'
        self._raw = raw
        self._safe = safe
        self._time = time
        self._proxy = proxy
        self._retry = retry
        self._rate = rate
        if e is not None :
            self._report_error(e, self._safe)

    def _delay(self, sec):
        time_module.sleep(sec)

    def _report_error(self, e, safe):
        type, value, traceback = sys.exc_info()
        kwargs = e.a if isinstance(e, PostmenException) else {'meta': {'message': str(e)}}
        if 'meta' not in kwargs:
            kwargs['meta'] = {}
        kwargs['meta']['traceback'] = traceback
        pe = PostmenException(**kwargs)
        if safe:
            self._error = pe
            return None
        _raise(pe, e, traceback)

    def _response(self, response, **kwargs):
        raw   = kwargs.get('raw', self._raw)
        time  = kwargs.get('time', self._time)

        # print response.headers
        # print response.text

        sec_before_reset = response.headers.get('x-ratelimit-reset', '0')
        sec_before_reset = int(sec_before_reset) / 1000
        #print sec_before_reset
        if sec_before_reset:
            if not self._time_before_reset or self._time_before_reset < sec_before_reset:
                self._time_before_reset = int(sec_before_reset)

        self._calls_left = response.headers.get('x-ratelimit-remaining', self._calls_left)
        if self._calls_left:
            self._calls_left = int(self._calls_left)

        # print 'self._time_before_reset', self._time_before_reset
        # print 'self._calls_left', self._calls_left

        if response.text:
            if raw:
                ret = response.text
            else:
                kls = JSONWithDatetimeDecoder if time else json.JSONDecoder
                try :
                    ret = json.loads(response.text, cls=kls)
                except ValueError as e :
                    error_message = "Something went wrong on Postmen's end"
                    raise PostmenException(message = error_message, code = 500)
                meta_code = ret.get('meta', {}).get('code', None)
                # print ret
                if not meta_code:
                    raise PostmenException(message='API response missed meta info', **ret)
                if int(meta_code) != 200 and int(meta_code / 1000) != 3:
                    raise PostmenException(**ret)
                if 'data' not in ret:
                    raise PostmenException(message='no data returned by API server', **ret)
                ret = ret['data']
        else:
            raise PostmenException(message='no response from API server')
        if not response.ok:
            raise PostmenException(message='HTTP code = %d' % response.status_code)
        return ret

    def _get_requests_params(self, method, path, **kwargs):
        proxy = kwargs.get('proxy', self._proxy)
        body  = kwargs.get('body', {})
        query = kwargs.get('query', {})
        endpoint = kwargs.get('endpoint', self._endpoint)

        headers = self._headers

        url = six.moves.urllib.parse.urljoin(
            endpoint,
            '%s/%s' % (self._version, path),
            allow_fragments=False
        )
        if body and not isinstance(body, six.string_types):
            body = json.dumps(body, cls=JSONWithDatetimeEncoder)
        if isinstance(query, dict):
            for key in list(query.keys()):
                value = query[key]
                if isinstance(value, datetime.datetime):
                    query[key] = value.isoformat()
        elif isinstance(query, six.string_types):
            if query[0] != '?' :
                query = '?%s' % query

        return {
            "method":  method,
            "url":     url,
            "params":  query,
            "headers": headers,
            "data":    body,
            "proxies": proxy
        }

    def _apply_rate_limit(self):
        if isinstance(self._calls_left, six.integer_types) and self._calls_left <= 0:
            # print 'self._time_before_reset', self._time_before_reset
            # print 'int(time_module.time())', int(time_module.time())
            delta = self._time_before_reset - int(time_module.time())
            if delta > 0:
                if not self._rate:
                    raise PostmenException(message = 'You have exceeded the API call rate limit. Please retry again at X-RateLimit-Reset header timestamp', code = 429, retryable = True)
                else :
                    # print 'apply delay', delta
                    self._delay(delta)

    def _call_ones(self, method, path, **kwargs):
        retry = kwargs.get('retry', self._retry)
        raw   = kwargs.get('raw', self._raw)
        safe  = kwargs.get('safe', self._safe)
        time  = kwargs.get('time', self._time)
        proxy = kwargs.get('proxy', self._proxy)
        tries = kwargs.get('tries', self._retries)
        self._error = None
        params = self._get_requests_params(method, path, **kwargs)
        self._apply_rate_limit()
        try:
            response = requests.request(**params)
        except Exception as e :
            raise PostmenException(message = 'Failed to perform HTTP request')
        return self._response(response, **kwargs)

    def call(self, method, path, **kwargs):
        """Create, perform HTTP call to Postmen API, parse and return result.

        :param method: HTTP method
        :type method: str or unicode
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, body, raw, safe, time, proxy, retry params
       
        :returns: API data response
        :rtype: dict or list or str or unicode
        
        :raises PostmenException: all errors and exceptions
        """
        retry  = kwargs.get('retry', self._retry)
        safe  = kwargs.get('safe', self._safe)
        tries = kwargs.get('tries', self._retries)
        count = 0
        delay = 0
        while True:
            try:
                return self._call_ones(method, path, **kwargs)
            except PostmenException as e:
                if not e.retryable() or not retry:
                    return self._report_error(e, safe)
                count = count + 1
                if count >= tries:
                    return self._report_error(e, safe)
                delay = 1.0 if delay == 0 else delay*2
                self._delay(delay)
            except Exception as e:
                return self._report_error(e, safe)

    def getError(self):
        """If safe == True, return last PostmenException"""
        return self._error

    def GET(self, path, **kwargs):
        """Create, perform HTTP GET call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from Postmen.call()
        
        :returns: same as Postmen.call()
        """
        return self.call('GET', path, **kwargs)

    def POST(self, path, **kwargs):
        """Create, perform HTTP POST call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from Postmen.call()
        
        :returns: same as Postmen.call()
        """
        return self.call('POST', path, **kwargs)

    def PUT(self, path, **kwargs):
        """Create, perform HTTP PUT call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from Postmen.call()
        
        :returns: same as Postmen.call()
        """
        return self.call('PUT', path, **kwargs)

    def DELETE(self, path, **kwargs):
        """Create, perform HTTP DELETE call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from Postmen.call()
        
        :returns: same as Postmen.call()
        """
        return self.call('DELETE', path, **kwargs)

    def get(self, resource, id_=None, **kwargs):
        """List all or retrieve particular resource (e.g. /labels, /labels/:id)
        
        :param resource: resource type (e.g. labels)
        :type resource: str or unicode
        :param id_: resource id, None to list all resources
        :type id_: str or unicode
        
        :returns: same as Postmen.call()
        """
        method = '%s/%s' % (resource, str(id_)) if id_ else resource
        return self.GET(method, **kwargs)

    def create(self, resource, payload, **kwargs):
        """Create resource object (e.g. label)
        
        :param resource: resource type (e.g. labels)
        :type resource: str or unicode
        :param payload: API call payload
        :type payload: dict or list or str or unicode
        
        :returns: same as Postmen.call()
        """
        kwargs['body'] = payload
        return self.POST(resource, **kwargs)
