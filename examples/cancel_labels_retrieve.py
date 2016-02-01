from credentials import *

# TODO put ID of a particular label
label = None

if label is None:
    print 'label is not set, modify cancel_labels_retrieve.py'

try:
    api = Postmen(key, region)
    # get all the cancelled labels
    result_all = api.create('cancel-labels')
    # get a particular cancelled label
    result_particular = api.create('cancel-labels', label)
    print "RESULT"
    print result_all
    print result_particular
except PostmenException as e:
    print "ERROR"
    print e.code()
    print e.message()
    print e.details()