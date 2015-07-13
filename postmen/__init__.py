import sys
import json
import time as time_module
import datetime
import traceback
import threading

import six
import requests
import dateutil.parser

__author__ = 'AfterShip <support@aftership.com>'


class JSONWithDatetimeEncoder(json.JSONEncoder):
    """Create JSON string as json.JSONEncoder, convert datetime.datetime objects to ISO format string"""
    def default(self, o):
        o = o.isoformat() if isinstance(o, datetime.datetime) else json.JSONEncoder.default(self, o)
        return o


class JSONWithDatetimeDecoder(json.JSONDecoder):
    """Parse JSON string as json.JSONDecoder, matched strings convert to datetime.datetime"""
    def decode(self, s):
        o = json.JSONDecoder.decode(self, s)
        return self.handleObj(o)

    def handleObj(self, o):
        if isinstance(o, dict):
            keys = list(o.keys())
            for key in keys:
                val = o[key]
                o[key] = self.handleObj(val)
            return o
        if isinstance(o, list):
            c = []
            for val in o:
                c.append(self.handleObj(val))
            return c
        if isinstance(o, six.string_types):
            try:
                return dateutil.parser.parse(o)
            except:
                pass
        return o


class PostmenError(Exception):
    """Postmen Errors. Include errors reported by API, related to API (e.g. rate limit) and other exceptions during API calls (e.g. HTTP connectivity issue)."""
    def __init__(self, **kwarg):
        self.meta = kwarg
        self._setDefault('code', None)
        self._setDefault('details', [])
        self._setDefault('retryable', False)
        self._setDefault('message', 'no details')

    def __str__(self):
        """Return string representation of error."""
        msg = self.message()+((' (%s)' % str(self.code())) if self.code() else "")
        return msg

    def _setDefault(self, key, default_value):
        if key not in self.meta:
            self.meta[key] = default_value

    def traceback(self):
        """Return traceback object of error. Traceback must be passed explicitly thru constructor method."""
        return self.meta['traceback']

    def code(self):
        """Return API error code. May return None if no error code were provided."""
        return self.meta['code']

    def message(self):
        """Return human readable error message."""
        return self.meta['message']

    def details(self):
        """Return API error details array."""
        return self.meta['details']

    def retryable(self):
        """Indicate if API call is retryable."""
        return self.meta['retryable']


class API(object):
    """API calls handler."""
    def __init__(
        self, api_key, region=None, endpoint=None, version='v3', x_agent='python-sdk-0.1',
        retries=4, raw=False, safe=False, time=False, proxy=None, retry=True
    ):
        """Handler constructor.

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
        :param safe: True to suppress exceptions. Use getError() instead
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
        kwargs = e.meta if isinstance(e, PostmenError) else {'message': str(e)}
        kwargs['traceback'] = traceback
        e = PostmenError(**kwargs)
        if safe:
            self._error = e
            return None
        raise e, None, traceback

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
                    raise PostmenError(message='API response missed meta info')

                # TODO: show Teddy, is error-identification correct?
                if int(meta_code / 1000) == 4:
                    raise PostmenError(**ret['meta'])
                if 'data' not in ret:
                    raise PostmenError(message='no data returned by API server')
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

    def _call(self,
              method,
              path,
              body=None,
              query=None,

              raw=None,
              safe=None,
              time=None,
              proxy=None,
              retry=None):
        
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
            except PostmenError, e:
                if not e.retryable():
                    return self._report_error(e, safe)
                count = count + 1
                if count >= tries:
                    return self._report_error(e, safe)

                delay = 1.0 if delay == 0 else delay*2
                self._delay(delay)
            except Exception, e:
                return self._report_error(e, safe)

    def getError(self):
        return self._error

    def GET(self, path, **kwargs):
        return self._call('GET', path, **kwargs)

    def POST(self, path, body, **kwargs):
        return self._call('POST', path, body, **kwargs)

    def PUT(self, path, body, **kwargs):
        return self._call('PUT', path, body, **kwargs)

    def DELETE(self, path, **kwargs):
        return self._call('DELETE', path, **kwargs)

    def get(self, resource, id_=None, **kwargs):
        method = '%s/%s' % (resource, str(id_)) if id_ else resource
        return self.GET(method, **kwargs)

    def create(self, resource, payload, **kwargs):
        return self.POST(resource, payload, **kwargs)

    def cancel(self, resource, id_, **kwargs):
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
    result = postmen.create('rates', payload_str)
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
        print('\ttraceback: %s\n' % e.traceback())
        traceback.print_tb(e.traceback())