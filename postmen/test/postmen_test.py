import pytest

import responses
import requests

from postmen import PostmenError
from postmen import API

headers  = "Date: Fri, 22 Jan 2016 04:05:30 GMT\r\n"
headers += "X-RateLimit-Limit: 10\r\n"
headers += "X-RateLimit-Remaining: 10\r\n"
headers += "X-RateLimit-Reset: 1453435538946\r\n"

headers_exceeded  = "Date: Fri, 22 Jan 2016 04:05:30 GMT\r\n"
headers_exceeded += "X-RateLimit-Limit: 10\r\n"
headers_exceeded += "X-RateLimit-Remaining: 0\r\n"
headers_exceeded += "X-RateLimit-Reset: 1453435538946\r\n"

headers_length = len(headers)
headers_length_exceeded = len(headers_exceeded)

global call

@responses.activate
def testRaiseException() :
    response = '{"meta":{"code":200,"message":"OK","details":[]},"data":{}}'
    head = {"x-ratelimit-reset": "1453435538946"}
    responses.add(responses.GET, 'https://REGION-api.postmen.com/v3/labels', adding_headers=head, body=response, status=200)
    api = API('KEY', 'REGION')
    api.get('labels')
    print "todo"
def testNonSerializableJSON():
    print "todo"
def testSafeModeEnabled():
    print "todo"
def testRaiseExceeded():
    print "todo"
def testRetryDelay():
    print "todo"
def testRetryMaxAttempt():
    print "todo"
def testRetryMaxAttemptExceeded():
    print "todo"
def testRetryPostmen():
    print "todo"
def testNotRetryPostmen():
    print "todo"
def testRateLimitExceeded():
    print "todo"
def testRateLimit():
    print "todo"
def testWrappers():
    print "todo"

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
