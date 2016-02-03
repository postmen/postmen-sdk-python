from credentials import *

# TODO put ID of a particular manifest
manifest = None

if manifest is None:
    print 'manifest is not set, modify manifests_retrieve.py'

try:
    api = Postmen(key, region)
    # get all manifests
    result_all = api.get('manifests')
    # get a particular manifest
    result_particular = api.get('manifests', manifest)
    print "RESULT"
    pp.pprint(result_all)
    pp.pprint(result_particular)
except PostmenException as e:
    print "ERROR"
    print e.code()
    print e.message()
    print e.details()
