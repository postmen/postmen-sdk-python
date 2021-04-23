from __future__ import print_function

import pytest
import traceback
import responses
import requests
import time

from datetime import datetime

from postmen import Postmen
from postmen import PostmenException

headers = {"x-ratelimit-reset": "1453435538946", "x-ratelimit-remaining": "10", "x-ratelimit-limit": "10"}
exceeded = {"x-ratelimit-reset": "1453435538946", "x-ratelimit-remaining": "0", "x-ratelimit-limit": "10"}
incorrect= {}

global call

# TEST 1
@responses.activate
def testNotRaiseException() :
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    api.get('labels')
    responses.reset()

# TEST 2
@responses.activate
def testNonSerializableJSON():
    response = 'THIS IS NOT A VALID JSON OBJECT'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200, content_type='text/plain')
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "Something went wrong on Postmen's end" in str(e.value)
    assert 500 == e.value.code()
    assert not e.value.retryable()

# TEST 3
@responses.activate
def testException3():
    response = '{"meta":{"code":999,"message":"PROBLEM","retryable":true,"details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "PROBLEM (999)" in str(e.value)
    assert 999 == e.value.code()
    assert e.value.retryable()

# TEST 4
@responses.activate
def testException4():
    response = '{"meta":{"code":999,"message":"PROBLEM","retryable":false,"details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "PROBLEM" in str(e.value.message())
    assert 999 == e.value.code()
    assert not e.value.retryable()

# TEST 5
@responses.activate
def testException5():
    response = '{"meta":{"code":999,"message":"PROBLEM","retryable":false,"details":[{"key":"value"}]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "PROBLEM" in str(e.value.message())
    assert 999 == e.value.code()
    assert not e.value.retryable()
    details = e.value.details()
    assert details[0]['key'] == 'value'

# TEST 6
@responses.activate
def testException6():
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = CrashPostmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "Failed to perform HTTP request" in str(e.value.message())
    assert not e.value.retryable()

# TEST 7
@responses.activate
def testArguments7():
    response = '{"meta":{"code":999,"message":"NOT OK","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200, content_type='text/plain')
    api = Postmen('KEY', 'REGION')
    api.get('labels', safe=True)
    responses.reset()
    e = api.getError()
    assert "NOT OK" in str(e.message())

# TEST 8
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
    responses.add_callback(responses.GET, 'https://region-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    api.get('labels')
    responses.reset()

# TEST 9
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
    responses.add_callback(responses.GET, 'https://region-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    before = time.time()
    api.get('labels')
    after = time.time()
    responses.reset()
    monkeypatch.setattr(time, 'sleep', lambda s: None)

# TEST 10
@responses.activate
def testRetryMaxAttemptExceeded(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    global call
    call = 0
    def request_callback(request):
        global call
        if call < 5 :
            call += 1
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":true, "details":[]},"data":{}}')
        else :
            pytest.fail("Maximum 5 attempts of retry, test #10 failed")
    responses.add_callback(responses.GET, 'https://region-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    assert "PROBLEM" in str(e.value.message())
    assert 999 == e.value.code()

# TEST 11
@responses.activate
def testArguments11(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    global call
    call = 0
    def request_callback(request):
        global call
        if call < 1 :
            call += 1
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":true, "details":[]},"data":{}}')
        else :
            pytest.fail("Shall not retry if retry = False, test #11 failed")
    responses.add_callback(responses.GET, 'https://region-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION', retry=False)
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    assert "PROBLEM" in str(e.value.message())
    assert 999 == e.value.code()
    assert e.value.retryable()

# TEST 12
@responses.activate
def testArgument12(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    global call
    call = 0
    def request_callback(request):
        global call
        if call == 0 :
            call = 1
            return (200, headers,  '{"meta":{"code":999,"message":"PROBLEM","retryable":false, "details":[]},"data":{}}')
        elif call == 1 :
            pytest.fail("Shall not retry if non retryable, test #12 failed")
    responses.add_callback(responses.GET, 'https://region-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    # print(e)
    assert "PROBLEM" in str(e.value.message())
    assert not e.value.retryable()
    monkeypatch.setattr(time, 'sleep', lambda s: None)

# TEST 13
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
    responses.add_callback(responses.GET, 'https://region-api.postmen.com/v3/labels', callback=request_callback)
    api = Postmen('KEY', 'REGION')
    api.get('labels')
    responses.reset()
    monkeypatch.setattr(time, 'sleep', lambda s: None)

# TEST 14
@responses.activate
def testArgument14():
    response = '{"meta":{"code":429,"message":"EXCEEDED","retryable":true, "details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=exceeded, body=response, status=200)
    api = Postmen('KEY', 'REGION', rate=False)
    with pytest.raises(PostmenException) as e:
        api.get('labels')
    responses.reset()
    assert "EXCEEDED" in str(e.value.message())
    assert 429 == e.value.code()
    assert e.value.retryable()

# TEST 15
@responses.activate
def testIncorrectResponseHeaders():
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{"key":"value"}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=incorrect, body=response, status=200)
    api = Postmen('KEY', 'REGION')
    ret = api.get('labels')
    assert ret['key'] == 'value'
    responses.reset()

# TEST 16
def testArgument16():
    proxies = {
        "http": "http://10.10.1.10:3128",
        "https": "http://10.10.1.10:1080",
    }
    api = OptionsPostmen('KEY', 'REGION', proxy=proxies)
    ret = api.get('resource')
    assert ret['proxy']['http']  == "http://10.10.1.10:3128"
    assert ret['proxy']['https'] == "http://10.10.1.10:1080"

# TEST 17
@responses.activate
def testArgument17() :
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION', raw=True)
    ret = api.get('labels')
    assert ret == response
    responses.reset()

# TEST 18
@responses.activate
def testArgument18() :
    response = '{"meta":{"code":999,"message":"NOT OK","details":[]},"data":{}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200)
    api = Postmen('KEY', 'REGION', raw=True)
    ret = api.get('labels')
    assert ret == response
    responses.reset()

def testWrappers():
    api = FakePostmen('KEY', 'REGION')
    payload = {'something': 'value'}
    body = 'THIS IS REQUEST BODY'
    # TEST 19
    ret = api.get('resource')
    assert ret['method'] == 'GET'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    # TEST 20
    ret = api.get('resource', 1234567890)
    assert ret['method'] == 'GET'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource/1234567890'
    # TEST 21
    ret = api.create('resource', body)
    assert ret['method'] == 'POST'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == 'THIS IS REQUEST BODY'
    # TEST 22
    ret = api.create('resource', payload)
    assert ret['method'] == 'POST'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == '{"something": "value"}'
    # TEST 23
    ret = api.GET('resource')
    assert ret['method'] == 'GET'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    # TEST 24
    ret = api.POST('resource', body = body)
    assert ret['method'] == 'POST'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == 'THIS IS REQUEST BODY'
    # TEST 25
    ret = api.POST('resource', body = payload)
    assert ret['method'] == 'POST'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == '{"something": "value"}'
    # TEST 26
    ret = api.PUT('resource', body=body)
    assert ret['method'] == 'PUT'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == 'THIS IS REQUEST BODY'
    # TEST 27
    ret = api.PUT('resource', body=payload)
    assert ret['method'] == 'PUT'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == '{"something": "value"}'
    # TEST 28
    ret = api.DELETE('resource',body=body)
    assert ret['method'] == 'DELETE'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == 'THIS IS REQUEST BODY'
    # TEST 29
    ret = api.DELETE('resource',body=payload)
    assert ret['method'] == 'DELETE'
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    assert ret['data'] == '{"something": "value"}'

# endpoint tests
def testEndpoints():
    api = FakePostmen('KEY', 'REGION')
    # TEST 30
    ret = api.get('resource')
    assert ret['url'] == 'https://REGION-api.postmen.com/v3/resource'
    # TEST 31
    ret = api.get('resource', endpoint='https://somedomain.com/')
    assert ret['url'] == 'https://somedomain.com/v3/resource'
    # TEST 32
    api = FakePostmen('KEY', 'REGION', endpoint='https://somedomain.com/')
    ret = api.get('resource')
    assert ret['url'] == 'https://somedomain.com/v3/resource'

# TEST 33
def testOptionalArgumentValues():
    api = OptionsPostmen('KEY', 'REGION')
    ret = api.get('resource')
    assert ret['retry'] == True
    assert ret['rate']  == True
    assert ret['raw']   == False
    assert ret['safe']  == False
    api = OptionsPostmen('KEY', 'REGION', retry=False, rate=False, raw=True, safe=True)
    ret = api.get('resource')
    assert ret['retry'] == False
    assert ret['rate']  == False
    assert ret['raw']   == True
    assert ret['safe']  == True
    ret = api.get('resource', retry=True, rate=True, raw=False, safe=False)
    assert ret['retry'] == True
    assert ret['rate']  == True
    assert ret['raw']   == False
    assert ret['safe']  == False

def testQuery():
    api = FakePostmen('KEY', 'REGION')
    payload = {'something': 'value'}
    body = 'THIS IS REQUEST BODY'
    # TEST 34
    ret = api.GET('resource', query=payload)
    assert ret['method'] == 'GET'
    assert ret['params']['something'] == 'value'
    # TEST 35
    ret = api.GET('resource', query={})
    assert ret['method'] == 'GET'
    assert ret['params'] == {}
    # TEST 36
    ret = api.GET('resource', query='?string')
    assert ret['method'] == 'GET'
    assert ret['params'] == '?string'
    # TEST 37
    ret = api.GET('resource', query='string')
    assert ret['method'] == 'GET'
    assert ret['params'] == '?string'

# TEST time (Python specific feature)
@responses.activate
def testTime():
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{"when": "2016-01-31T16:45:46+00:00"}}'
    responses.add(responses.GET, 'https://region-api.postmen.com/v3/labels', adding_headers=headers, body=response, status=200, content_type='text/plain')
    api = Postmen('KEY', 'REGION')
    res = api.get('labels')
    assert res['when'] == '2016-01-31T16:45:46+00:00'
    res = api.get('labels', time=True)
    assert isinstance(res['when'], datetime)
    api = Postmen('KEY', 'REGION', time=True)
    res = api.get('labels', time=True)
    assert isinstance(res['when'], datetime)
    assert res['when'].year == 2016
    assert res['when'].month == 1
    assert res['when'].day == 31
    assert res['when'].hour == 16
    assert res['when'].minute == 45
    assert res['when'].second == 46
    responses.reset()

class OptionsPostmen(Postmen):
    def __init__(self, *args, **kwargs):
        super(OptionsPostmen, self).__init__(*args, **kwargs)

    def _call_ones(self, method, path, **kwargs):
        retry = kwargs.get('retry', self._retry)
        rate  = kwargs.get('rate', self._rate);
        raw   = kwargs.get('raw', self._raw)
        safe  = kwargs.get('safe', self._safe)
        time  = kwargs.get('time', self._time)
        proxy = kwargs.get('proxy', self._proxy)
        body  = kwargs.get('body', {})
        query = kwargs.get('query', {})
        return {
                "retry": retry,
                "rate": rate,
                "raw": raw,
                "safe": safe,
                "time": time,
                "proxy": proxy,
                "body": body,
                "query": query
                }

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
        return self._wrap_response(response, **kwargs)

    def _wrap_request(self, **kwargs):
        return kwargs

    def _wrap_response(self, response, **kwargs):
        return response

class CrashPostmen(Postmen):
    def __init__(self, *args, **kwargs):
        super(CrashPostmen, self).__init__(*args, **kwargs)

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
        try:
            response = self._wrap_request(**params)
        except Exception as e :
            raise PostmenException(message = 'Failed to perform HTTP request')
        return self._response(response, **kwargs)

    def _wrap_request(self, **kwargs):
        raise Exception('requests failed')
