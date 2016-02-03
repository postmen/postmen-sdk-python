from credentials import *

# follow proxy scheme used in requests library
# for more info
# http://docs.python-requests.org/en/latest/user/advanced/#proxies
proxies = {
    "http": "http://10.10.1.10:3128",
    "https": "http://10.10.1.10:1080"
}

try:
    api = Postmen(key, region, proxy = proxies)
    result = api.get('labels')
    print "RESULT"
    pp.pprint(result)
except PostmenException as e:
    print "ERROR"
    print e.code()
    print e.message()
    print e.details()
