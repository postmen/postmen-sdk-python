"""API and PostmenError classes are intended for SDK users.
"""

import sys
import json
import time as time_module
import datetime
import traceback
import threading

import six
import requests

from jsont import JSONWithDatetimeEncoder
from jsont import JSONWithDatetimeDecoder
if six.PY2:
    from rp2 import _raise
else:
    from rp3 import _raise

__author__ = 'Postmen <support@postmen.com>'


class PostmenError(Exception):
    """Include errors reported by API, related to API (e.g. rate limit) and other exceptions during API calls (e.g. HTTP connectivity issue)."""
    def __init__(self, message=None, **kwarg):
        self.a = kwarg
        if 'meta' not in self.a:
            self.a['meta'] = {}
        if 'data' not in self.a:
            self.a['data'] = None
        if message:
            self.a['meta']['message'] = message
        self._setDefault('code', None)
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

class API(object):
    """API calls handler.

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
    :type proxy: str or unicode
    :param retry: True to retry calls in case of retriable errors
    :type retry: bool
    
    :raises PostmenError: if API is missed
    :raises PostmenError: if region or endpoint is missed
    :raises PostmenError: if version is missed
    """
    def __init__(
        self, api_key, region=None, endpoint=None, version='v3', x_agent='python-sdk-0.4',
        retries=4, raw=False, safe=False, time=False, proxy=None, retry=True
    ):
        if not api_key:
            raise PostmenError(message='missed API key')
        if not region and not endpoint:
            raise PostmenError(message='missed region')
        if not version:
            raise PostmenError(message='missed API version')
        self._retries = retries
        self._error = None
        self._version = version
        self._calls_left = None
        self._time_before_reset = None
        self._endpoint = endpoint if endpoint else 'https://%s-api.postmen.com' % region
        self._headers = {'content-type': 'application/json'}
        self._headers['postmen-api-key'] = api_key
        self._headers['x-postmen-agent'] = x_agent
        self._raw = raw
        self._safe = safe
        self._time = time
        self._proxy = {'https': proxy} if proxy else {}
        self._retry = retry

    def _delay(self, sec):
        time_module.sleep(sec)

    def _report_error(self, e, safe):
        type, value, traceback = sys.exc_info()
        kwargs = e.a if isinstance(e, PostmenError) else {'meta': {'message': str(e)}}
        if 'meta' not in kwargs:
            kwargs['meta'] = {}
        kwargs['meta']['traceback'] = traceback
        pe = PostmenError(**kwargs)
        if safe:
            self._error = pe
            return None
        _raise(pe, e, traceback)

    def _response(self, response, raw, time):
        sec_before_reset = response.headers.get('x-ratelimit-reset', None)
        if sec_before_reset:
            self._time_before_reset = time_module.clock() + float(sec_before_reset)
        
        self._calls_left = response.headers.get('x-ratelimit-remaining', self._calls_left)
        if self._calls_left:
            self._calls_left = int(self._calls_left)        

        if response.text:
            if raw:
                ret = response.text
            else:
                kls = JSONWithDatetimeDecoder if time else json.JSONDecoder
                ret = json.loads(response.text, cls=kls)
                meta_code = ret.get('meta', {}).get('code', None)
                if not meta_code:
                    raise PostmenError(message='API response missed meta info', **ret)
                if int(meta_code / 1000) == 4:
                    raise PostmenError(**ret)
                if 'data' not in ret:
                    raise PostmenError(message='no data returned by API server', **ret)
                ret = ret['data']
        else:
            raise PostmenError(message='no response from API server')
        if not response.ok:
            raise PostmenError(message='HTTP code = %d' % response.status_code)
        return ret

    def _get_requests_params(self, method, path, body, query, proxy):
        headers = self._headers

        url = six.moves.urllib.parse.urljoin(
            self._endpoint,
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
            delta = self._time_before_reset - time_module.clock()
            if delta > 0:
                self._delay(delta)

    def _call_ones(self, method, path, body, query, raw, time, proxy):
        self._error = None
        params = self._get_requests_params(method, path, body, query, proxy)
        self._apply_rate_limit()
        response = requests.request(**params)
        return self._response(response, raw, time)

    def call(
        self, method, path, body,
        query=None, raw=None, safe=None, time=None, proxy=None, retry=None
    ):
        """Create, perform HTTP call to Postmen API, parse and return result.

        :param method: HTTP method
        :type method: str or unicode
        :param path: URL path
        :type path: str or unicode
        :param body: API call payload
        :type body: dict or list or str or unicode
        :param query: URL query
        :type query: dict or str or unicode
        :param raw: True to exclude parsing of response JSON strings (overwrite constructor value)
        :type raw: bool
        :param safe: True to suppress exceptions. Use getError() instead (overwrite constructor value)
        :type safe: bool
        :param time: True to convert ISO time strings to datetime.datetime (overwrite constructor value)
        :type time: bool
        :param proxy: Proxy for HTTP calls (overwrite constructor value)
        :type proxy: str or unicode
        :param retry: True to retry calls in case of retriable errors (overwrite constructor value)
        :type retry: bool
        
        :returns: API data response
        :rtype: dict or list or str or unicode
        
        :raises PostmenError: all errors and exceptions
        """
        retry = self._retry if retry==None else retry
        raw   = self._raw   if raw==None   else raw
        safe  = self._safe  if safe==None  else safe
        time  = self._time  if time==None  else time
        if proxy == False:
            proxy = {}
        elif isinstance(proxy, six.string_types):
            proxy = {'https': proxy}
        else:
            proxy = self._proxy
        tries = self._retries if retry else 1
        count = 0
        delay = 0
        while True:
            try:
                return self._call_ones(method, path, body, query, raw, time, proxy)
            except PostmenError as e:
                if not e.retryable():
                    return self._report_error(e, safe)
                count = count + 1
                if count >= tries:
                    return self._report_error(e, safe)
                delay = 1.0 if delay == 0 else delay*2
                self._delay(delay)
            except Exception as e:
                return self._report_error(e, safe)

    def getError(self):
        """If safe == True, return last PostmenError"""
        return self._error

    def GET(self, path, **kwargs):
        """Create, perform HTTP GET call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from API.call()
        
        :returns: same as API.call()
        """
        return self.call('GET', path, None, **kwargs)

    def POST(self, path, body, **kwargs):
        """Create, perform HTTP POST call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param body: API call payload
        :type body: dict or list or str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from API.call()
        
        :returns: same as API.call()
        """
        return self.call('POST', path, body, **kwargs)

    def PUT(self, path, body, **kwargs):
        """Create, perform HTTP PUT call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param body: API call payload
        :type body: dict or list or str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from API.call()
        
        :returns: same as API.call()
        """
        return self.call('PUT', path, body, **kwargs)

    def DELETE(self, path, **kwargs):
        """Create, perform HTTP DELETE call to Postmen API, parse and return result.
        
        :param path: URL path
        :type path: str or unicode
        :param **kwargs: query, raw, safe, time, proxy, retry params from API.call()
        
        :returns: same as API.call()
        """
        return self.call('DELETE', path, None, **kwargs)

    def get(self, resource, id_=None, **kwargs):
        """List all or retrieve particular resource (e.g. /labels, /labels/:id)
        
        :param resource: resource type (e.g. labels)
        :type resource: str or unicode
        :param id_: resource id, None to list all resources
        :type id_: str or unicode
        
        :returns: same as API.call()
        """
        method = '%s/%s' % (resource, str(id_)) if id_ else resource
        return self.GET(method, **kwargs)

    def create(self, resource, payload, **kwargs):
        """Create resource object (e.g. label)
        
        :param resource: resource type (e.g. labels)
        :type resource: str or unicode
        :param payload: API call payload
        :type payload: dict or list or str or unicode
        
        :returns: same as API.call()
        """
        return self.POST(resource, payload, **kwargs)

    def cancel(self, resource, id_, **kwargs):
        """Delete/cancel particular resource (e.g. label)
        
        :param resource: resource type (e.g. labels)
        :type resource: str or unicode
        :param id_: resource id
        :type id_: str or unicode
        
        :returns: same as API.call()
        """
        return self.POST('%s/%s/cancel' % (resource, str(id_)), '{"async":false}', **kwargs)


if __name__ == "__main__":
    print("Smoke test")
    region = 'sandbox'
    api_key = 'API_KEY'
    shipper_id = 'SHIPPER_ACCOUNT_ID'
    payload = {
        "async": False,
        "shipper_accounts": [{
            "id": shipper_id
        }],
        "is_document": False,
        "shipment": {
            "ship_from": {
                "contact_name": "Jameson McLaughlin",
                "company_name": "Bode, Lind and Powlowski",
                "street1": "8918 Borer Ramp",
                "city": "Los Angeles",
                "state": "CA",
                "postal_code": "90001",
                "country": "USA",
                "type": "business"
            },
            "ship_to": {
                "contact_name": "Dr. Moises Corwin",
                "phone": "1-140-225-6410",
                "email": "Giovanna42@yahoo.com",
                "street1": "28292 Daugherty Orchard",
                "city": "Beverly Hills",
                "postal_code": "90209",
                "state": "CA",
                "country": "USA",
                "type": "residential"
            },
            "parcels": [{
                "description": "iMac (Retina 5K, 27-inch, Late 2014)",
                "box_type": "custom",
                "weight": {
                    "value": 9.54,
                    "unit": "kg"
                },
                "dimension": {
                    "width": 65,
                    "height": 52,
                    "depth": 21,
                    "unit": "cm"
                },
                "items": [{
                    "description": "iMac (Retina 5K, 27-inch, Late 2014)",
                    "origin_country": "USA",
                    "quantity": 1,
                    "price": {
                        "amount": 1999,
                        "currency": "USD"
                    },
                    "weight": {
                        "value": 9.54,
                        "unit": "kg"
                    },
                    "sku": "imac2014"
                }]
            }]
        }
    }
    postmen = API(api_key, region)
    result = postmen.get('labels')
    print('\nRESULT:')
    print(json.dumps(result, indent=4, cls=JSONWithDatetimeEncoder))
    e = postmen.getError();
    if e:
        print('\nERROR:')
        print('\t%s' % str(e))
        print('\tcode: %s' % e.code())
        print('\tmessage: %s' % e.message())
        print('\tdetails: %s' % e.details())
        print('\tretryable: %s' % e.retryable())
        print('\tdata: %s' % e.data())
        print('\ttraceback: %s\n' % e.traceback())
        traceback.print_tb(e.traceback())