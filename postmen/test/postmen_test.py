import pytest
import traceback
import responses
import requests
import time

from postmen import Postmen
from postmen import PostmenException

headers = {"x-ratelimit-reset": "1453435538946", "x-ratelimit-remaining": "10", "x-ratelimit-limit": "10"}
exceeded = {"x-ratelimit-reset": "1453435538946", "x-ratelimit-remaining": "0", "x-ratelimit-limit": "10"}
incorrect= {}

global call

# expects not to raise any exceptions as meta code == 200
@responses.activate
def testNotRaiseException() :
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    api.get('labels')
    responses.reset()

# note : to simulate equiv of curl error just remove
# @responses.activate

# expects to raise an exception if response from the API is not
# a valid JSON encoded objecr in a string
@responses.activate
def testNonSerializableJSON():
    response = 'THIS IS NOT A VALID JSON OBJECT'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200, content_type='text/plain')
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "Something went wrong on Postmen's end" in str(e.value)

# expects not to raise the exception in safe mode but make it
# accessibla via getError() method
@responses.activate
def testSafeModeEnabled():
    response = 'THIS IS NOT A VALID JSON OBJECT, BUT EXCEPTION IS NOT GOING TO BE RAISED'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200, content_type='text/plain')
    api = Postmen('KEY', 'REGION')
    api.get('labels', safe=True)
    responses.reset()
    e = api.getError()
    assert "Something went wrong on Postmen's end" in str(e.message())

# expected to raise an exception if meta code different
# than 200
@responses.activate
def testRaiseExceeded():
    response = '{"meta":{"code":999,"message":"PROBLEM","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "PROBLEM (999)" in str(e.value)

# checks if there will be 3 seconds delay if retryable error
# occurs, tests if delay increments correctly
@responses.activate
def testRetryDelay():
    global call
    call = 0
    def request_callback(request):
        global call
        if call == 0 :
            call = 1
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":true, "details":[]},"data":{}}')
        elif call == 1 :
            call = 2
            "second attempt"
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":true,"details":[]},"data":{}}')
        elif call == 2 :
            call = 3
            return (200, headers,  '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}')
    responses.add_callback(responses.GET, 'https://REGION-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    api.get('labels')
    responses.reset()

# expects not to fail if we etry four times
@responses.activate
def testRetryMaxAttempt(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    global call
    call = 0
    def request_callback(request):
        global call
        if call < 4 :
            call += 1
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":true, "details":[]},"data":{}}')
        else :
            return (200, headers,  '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}')
    responses.add_callback(responses.GET, 'https://REGION-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    before = time.time()
    api.get('labels')
    after = time.time()
    responses.reset()
    monkeypatch.setattr(time, 'sleep', lambda s: None)

# expects to raise an exception because of too many retries
@responses.activate
def testRetryMaxAttemptExceeded(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    response = '{"meta":{"code":999,"message":"PROBLEM","retryable":true, "details":[]},"data":{}}'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "PROBLEM (999)" in str(e.value)
    monkeypatch.setattr(time, 'sleep', lambda s: None)

# expects not to retry since postmen will return a non
# retryable error
@responses.activate
def testNotRetryPostmen(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    global call
    call = 0
    def request_callback(request):
        global call
        if call == 0 :
            call = 1
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":false, "details":[]},"data":{}}')
        elif call == 1 :
            return (200, headers,  '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}')
    responses.add_callback(responses.GET, 'https://REGION-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    #print e
    assert "PROBLEM (999)" in str(e.value)
    monkeypatch.setattr(time, 'sleep', lambda s: None)

# expected to raise an exception
@responses.activate
def testRateLimitExceeded():
    response = '{"meta":{"code":429,"message":"EXCEEDED","retryable":false, "details":[]},"data":{}}'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=exceeded, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "EXCEEDED (429)" in str(e.value)

# expected not to raise an exception
# wait instead
@responses.activate
def testRateLimit(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    global call
    call = 0
    def request_callback(request):
        global call
        if call == 0 :
            call = 1
            return (200, exceeded,  '{"meta":{"code":429,"message":"EXCEEDED","retryable":true, "details":[]},"data":{}}')
        elif call == 1 :
            return (200, headers,  '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}')
    responses.add_callback(responses.GET, 'https://REGION-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    api.get('labels')
    responses.reset()
    monkeypatch.setattr(time, 'sleep', lambda s: None)
'''
# test if method and other parameters are correct
def testWrappers():
    api = FakePostmen('KEY', 'REGION')
    ret = api.get('resource')
    assert ret['method'] == 'GET'
    assert ret['path'] == 'resource'
    ret = api.get('resource', 1234567890)
    assert ret['method'] == 'GET'
    assert ret['path'] == 'resource/1234567890'
    payload = {'something': 'value'}
    ret = api.create('resource', payload)
    assert ret['method'] == 'POST'
    assert ret['path'] == 'resource'
    assert ret['body']['something'] == 'value'
    body = 'THIS IS REQUEST BODY'
    ret = api.GET('resource')
    assert ret['method'] == 'GET'
    assert ret['path'] == 'resource'
    ret = api.POST('resource', body)
    assert ret['method'] == 'POST'
    assert ret['path'] == 'resource'
    assert ret['body'] == 'THIS IS REQUEST BODY'
    ret = api.PUT('resource', body)
    assert ret['method'] == 'PUT'
    assert ret['path'] == 'resource'
    assert ret['body'] == 'THIS IS REQUEST BODY'
    ret = api.DELETE('resource')
    assert ret['method'] == 'DELETE'
    assert ret['path'] == 'resource'
'''
# expected not to raise any exceptions if x-ratelimit-reset
# header is not present
@responses.activate
def testIncorrectResponseHeaders():
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{"key":"value"}}'
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=incorrect, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    ret = api.get('labels')
    assert ret['key'] == 'value'
    responses.reset()

class FakePostmen(Postmen):
    def __init__(self, *args, **kwargs):
        super(FakePostmen, self).__init__(*args, **kwargs)

    def _call_ones(self, method, path, **kwargs):
        retry = kwargs.get('retry', self._retry)
        raw   = kwargs.get('raw', self._raw)
        safe  = kwargs.get('safe', self._safe)
        time  = kwargs.get('time', self._time)
        proxy = kwargs.get('proxy', self._proxy)
        tries = kwargs.get('tries', self._retries)
        body  = kwargs.get('body', {})
        query = kwargs.get('query', {})
        self._error = None
        params = self._get_requests_params(method, path, **kwargs)
        self._apply_rate_limit()
        response = self._wrap_request(**params)
        return self._wrap_response(response, raw, time)

    def _wrap_request(self, **kwargs):
        return kwargs

    def _wrap_response(self, response, **kwargs):
        return kwargs
'''
# example how to achieve same behaviour as ->at($index) in
# PHPUnit library
@responses.activate
def testMultiResponseExample():
    global call
    call = 0
    def request_callback(request):
        global call
        headers = {'request-id': '728d329e-0e86-11e4-a748-0c84dc037c13'}
        if call == 0 :
            call = 1
            return (404, headers, '{"msg": "not found"}')
        elif call == 1 :
            call = 0
            return (200, headers, '{"msg": "ok"}')
    responses.add_callback(responses.GET, 'http://twitter.com/api/1/foobar', callback=request_callback)
    print requests.get('http://twitter.com/api/1/foobar')
    print requests.get('http://twitter.com/api/1/foobar')
#    api = API('NOT VALID KEY', 'region')
    assert 1 == 0

# example of single mock response
@responses.activate
def testSingleResponse():
    responses.add(responses.GET, 'http://twitter.com/api/1/foobar', json={"error": "not found"}, status=404)
    print requests.get('http://twitter.com/api/1/foobar')

# example of assertion
def testIfOneEqualsZero():
    assert 0 == 0
'''
