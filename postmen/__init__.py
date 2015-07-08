import json
import time
import threading
import datetime
import dateutil.parser
import sys
import pkg_resources

import requests
import six
import six.moves.urllib.parse as urllib_parse

__author__ = 'AfterShip <support@aftership.com>'

# sdk_ver = pkg_resources.require("postmen")[0].version
sdk_ver = '0.1'


class PostmenError(Exception):
    def __init__(self, **kwarg):
        self.meta = kwarg
        self._setDefault('code', None)
        self._setDefault('details', [])
        self._setDefault('retryable', False)
        self._setDefault('message', 'no details')
        print('PostmenError constructor: '+json.dumps(self.meta, indent=4))

    def __getitem__(self, attribute):
        return self.meta[attribute]

    def __str__(self):
        return self.message()+' '+( ("("+self.code()+")") if self.code() else "" )

    def _setDefault(self, key, default_value):
        if key not in self.meta:
            self.meta[key] = default_value

    def code(self):
        return self['code']

    def message(self):
        return self['message']

    def details(self):
        return self['details']

    def retryable(self):
        return self['retryable']


class JSONWithDatetimeEncoder(json.JSONEncoder):
    def default(self, o):
        o = o.isoformat() if isinstance(o, datetime.datetime) else json.JSONEncoder.default(self, o)
        return o


class JSONWithDatetimeDecoder(json.JSONDecoder):
    def decode(self, s):
        o = json.JSONDecoder.decode(self, s)
        return self.handleObj(o)

    def handleObj(self, o):
        if isinstance(o, dict):
            for key in list(o.keys()):
                val = o[key]
                o[key] = self.handleObj(val)
            return o
        if isinstance(o, list):
            collection = []
            for val in o:
                collection.append(self.handleObj(val))
            return collection
        if isinstance(o, six.string_types):
            try:
                return dateutil.parser.parse(o)
            except:
                pass
        return o


class API(object):
    """
    Test code goes below.

    Test covers all accessing methods (POST, GET, PUT, DELETE).
    Test covers all variants of building specific API calls (endpoints paths + body):
    - dot.separated.constants.get()                : GET /dot/separated/constants
    - params['in']['brackets'].get()               : GET /params/in/brackets
    - path.get('arg1', 'arg2', arg_name='arg3')    : GET /path/arg1/arg2?arg_name=arg3
    Test checks conversion of input list type parameters to comma separated strings.
    Test checks conversion of input timestamp strings to datetime variables.
    Test checks conversion of output timestamp strings to datetime variables.


    >>> api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))['tracking']['title']
    u'Title'
    >>> api.trackings.get(slug, number, fields=['title', 'created_at'])['tracking']['title']
    u'Title'
    >>> type(api.trackings.put(slug, number, tracking=dict(title="Title (changed)"))['tracking']['updated_at'])
    <type 'datetime.datetime'>
    >>> api.trackings[slug][number].get()['tracking']['title']
    u'Title (changed)'
    >>> api.trackings.get(created_at_min=datetime.datetime(2014, 6, 1), fields=['title', 'order_id'])['fields']
    u'title,order_id'
    >>> api.trackings.delete(slug, number)['tracking']['slug']
    u'russian-post'
    """
    def __init__(self, api_key, region=None,
                 endpoint=None, version='v3', proxy=None, retry=True, datetime_convert=False):
        if not api_key:
            raise PostmenError(message='missed API key')
        if not region and not endpoint:
            raise PostmenError(message='missed region')
        if region and not endpoint:
            endpoint = 'https://%s-api.postmen.com' % region
        max_calls_per_sec = 1  # Pass as a named argument?
        self._error = None
        self._retry = retry
        self._version = version
        self._endpoint = endpoint
        self._last_call = None
        self._rate_limit = 1.0 / float(max_calls_per_sec)
        self._datetime_convert = datetime_convert
        self._proxies = {'https': proxy} if proxy else None
        self._headers = {
            'content-type': 'application/json',
            'postmen-api-key': api_key,
            'x-postmen-agent': 'python-sdk-%s' % sdk_ver
        }

    def _response(self, response, raw):
        if response.text:
            if raw:
                ret = response.text
            else:
                if self._datetime_convert:
                    kls = JSONWithDatetimeDecoder
                else:
                    kls = json.JSONDecoder
                ret = json.loads(response.text, cls=kls)

                meta_code = ret.get('meta', {}).get('code', None)
                if not meta_code:
                    raise PostmenError(message='API response missed meta info')

                if meta_code != 200:
                    raise PostmenError(**ret['meta'])
        else:
            ret = None
        if not response.ok:
            raise PostmenError(message='HTTP code = %d' % response.status_code)
        if not ret:
            raise PostmenError(message='no response from API server')
        return ret['data']

    def _apply_rate_limit(self):
        with threading.Lock():
            if self._last_call:
                delta = self._rate_limit - (time.clock() - self._last_call)
                if delta > 0:
                    time.sleep(delta)
            self._last_call = time.clock()

    def _get_requests_params(self, method, path, body, query):
        headers = self._headers
        url = urllib_parse.urljoin(self._endpoint, self._version+'/'+path, allow_fragments=False)
        if not isinstance(body, six.string_types):
            body = json.dumps(body, cls=JSONWithDatetimeEncoder)
        if query:
            for key in list(query.keys()):
                value = query[key]
                if isinstance(value, datetime.datetime):
                    query[key] = value.isoformat()

        return {
            "method": method,
            "url": url,
            "params": query,
            "headers": headers,
            "data": body,
            "proxies": self._proxies
        }

    def _call_ones(self, method, path, body, query, raw):
        self._error = None
        params = self._get_requests_params(method, path, body, query)
        self._apply_rate_limit()
        try:
            response = requests.request(**params)
        except Exception, e:
            raise PostmenError(message=str(e))
        return self._response(response, raw)
    
    def _call(self, method, path, body=None, query={}, retry=None, raw=False, safe=False):
        retry = self._retry if retry==None else retry

        tries = 5 if retry else 1
        count = 0
        delay = 0

        while True:
            try:
                return self._call_ones(method, path, body, query, raw)
            except PostmenError, e:
                if not e.retryable():
                    raise

                count = count + 1
                if count >= tries:
                    raise
                delay = 1.0 if delay == 0 else delay*2
                time.sleep(delay)
            except Exception, e:
                type, value, traceback = sys.exc_info()
                raise PostmenError, ("unexpected error", type, value), traceback

    def getError():
        return self._error

    def GET(self, path, **kwargs):
        return self._call('get', path, **kwargs)

    def POST(self, path, body, **kwargs):
        return self._call('post', path, body, **kwargs)

    def PUT(self, path, body, **kwargs):
        return self._call('put', path, body, **kwargs)

    def DELETE(self, path, **kwargs):
        return self._call('delete', path, **kwargs)

    def get(self, resource, id=None, **kwargs):
        method = '%s/%s'%(method, str(id)) if id else resource
        return self.GET(method, **kwargs)

    def create(self, resource, payload, **kwargs):
        return self.POST(resource, payload, **kwargs)

    def cancel(self, resource, id_, **kwargs):
        return self.POST(resource+'/'+id_+'/cancel', '{"async":false}', **kwargs)


if __name__ == "__main__":
    import doctest
    print("Running smoke tests")
    # doctest.testmod(extraglobs={'slug': TEST_SLUG,
    #                             'number': TEST_TRACKING_NUMBER,
    #                             'api': APIv4(TEST_API_KEY)})

    api_key = 'API_KEY'
    region = 'sandbox'
    payload = {
        "async": False,
        "shipper_accounts": [{
            "id": "SHIPPER_ACCOUNTS.ID"
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


    postmen = API(api_key, region, datetime_convert=True)
    result = postmen.create('rates', payload)
    print( json.dumps(result, indent=4, cls=JSONWithDatetimeEncoder) )

    print("done!")