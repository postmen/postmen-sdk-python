from __future__ import print_function

from credentials import *

# TODO put ID of your shipper account
shipper = None

if shipper is None:
    print('shipper is not set, modify labels_create.py')

parcel = {
    'description': 'info about the parcel',
    'box_type': 'custom',
    'weight': {
        'value': 1.5,
        'unit': 'kg'
    },
    'dimension': {
        'width': 20,
        'height': 30,
        'depth': 40,
        'unit': 'cm'
    },
    'items': [
        {
            'description': 'Food Bar',
            'hs_code': '11111111',
            'origin_country': 'USA',
            'price':
                {
                    'amount': 50,
                    'currency': u'USD'
                },
            'quantity': 2,
            'sku': 'Epic_Food_Bar',
            'weight': {
                'unit': u'kg',
                'value': 0.6
            }
        }
    ]
}

sender = {
    'contact_name': 'your name',
    'company_name': 'name of your company',
    'street1': 'your address',
    'street2': None,
    'street3': None,
    'city': 'your city',
    'state': 'your state',
    'postal_code': 'your postal code',
    'country': 'HKG',
    'phone': '1-403-504-5496',
    'fax': '1-403-504-5497',
    'fax_id': None,
    'email': 'test@test.test',
    'type': 'business'
}

receiver = {
    'contact_name': 'Rick McLeod (RM Consulting)',
    'street1': '71 Terrace Crescent NE',
    'street2': 'This is the second streeet',
    'city': 'Medicine Hat',
    'state': 'Alberta',
    'postal_code': 'T1C1Z9',
    'country': 'RUS',
    'phone': '1-403-504-5496',
    'email': 'test@test.test',
    'type': 'residential'
}

payload = {
    'is_document': False,
    'return_shipment': False,
    'paper_size': 'default',
    'service_type': 'spsr_intl',
    'customs': {
        'billing': {
            'paid_by': 'shipper',
            'method': {
                'account_number': '950000002',
                'type': 'account',
            }
        },
        'purpose': 'gift'
    },
    'shipper_account': {
        'id': shipper,
    },
    'shipment': {
        'parcels': [
    		parcel
    	],
        'ship_from': sender,
        'ship_to': receiver
    }
}

try:
    api = Postmen(key, region)
    result = api.create('labels', payload)
    print("RESULT")
    pp.pprint(result)
except PostmenException as e:
    print("ERROR")
    print(e.code())
    print(e.message())
    print(e.details())
