from credentials import *

# TODO put ID of a particular rate
rate = None

if rate is None:
    print 'rate is not set, modify rates_retrieve.py'

try:
    api = Postmen(key, region)
    # get all rates
    result_all = api.create('rates')
    # get a particular rate
    result_particular = api.create('rates', rate)
    print "RESULT"
    print result_all
    print result_particular
except PostmenException as e:
    print "ERROR"
    print e.code()
    print e.message()
    print e.details()
