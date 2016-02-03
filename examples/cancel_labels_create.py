from credentials import *

# TODO put ID of the label you wish to cancel
label = None

if label is None:
    print 'label is not set, modify cancel_labels_create.py'

payload = {
    'label': {
	'id': label
    }
}

try:
    api = Postmen(key, region)
    result = api.create('cancel-labels', payload)
    print "RESULT"
    pp.pprint(result)
except PostmenException as e:
    print "ERROR"
    print e.code()
    print e.message()
    print e.details()
