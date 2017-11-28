from __future__ import print_function

from credentials import *

# TODO put ID of your shipper account
shipper = None

if shipper is None:
    print('shipper is not set, modify manifests_create.py')

payload = {
    'shipper_account': {
	'id': shipper
    },
    'async': False
}

try:
    api = Postmen(key, region)
    result = api.create('manifests', payload)
    print("RESULT")
    pp.pprint(result)
except PostmenException as e:
    print("ERROR")
    print(e.code())
    print(e.message())
    print(e.details())
