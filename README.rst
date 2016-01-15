About
=====

Easiest way to integrate with multiple shipping carriers for online retailers and marketplaces of any size.

Add shipping functionality to your application for printing labels, calculating rates and submitting manifests.

Installation
============

Via pip
-------

Run the following:

.. code-block:: bash

    $ pip install postmen

Via source code
---------------

Download the code archive, unzip it, create/activate `virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`_, go to the source root directory, then run:

.. code-block:: bash

    $ python setup.py install

Usage
=====

Rates
-----

Calculate rates

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION')
    item = {
        'sku': 'PS4-2015',
        'origin_country': 'JPN',
        'description': 'PS4',
        'weight': {
            'unit': 'kg',
            'value': 0.6
        },
        'price': {
            'currency': 'JPY',
            'amount': 50
        },
        'quantity': 2
    }
    sender = {
        'city': 'Hung Hom',
        'street1': 'Flat A, 29/F, Block 17 Laguna Verde',
        'phone': '96679797',
        'state': 'Kowloon',
        'country': 'HKG',
        'contact_name': 'Yin Ting Wong',
        'type': 'residential',
        'email': 'test@test.test'
    }
    receiver = {
        'city': 'Yorktown',
        'street1': '9504 W Smith ST',
        'phone': '7657168649',
        'state': 'Indiana',
        'postal_code': '47396',
        'country': 'USA',
        'contact_name': 'Mike Carunchia',
        'type': 'residential',
        'email': 'test@test.test'
    }
    query = {
        'async': False,
        'shipment': {
            'ship_from': sender,
            'ship_to': receiver,
            'parcels': [
                {
                    'items': [
                        item
                    ],
                    'weight': {
                        'unit': 'kg',
                        'value': 0.5
                    },
                    'box_type': 'custom',
                    'dimension': {
                        'width': 20,
                        'depth': 10,
                        'unit': 'cm',
                        'height': 10
                    }
                }
            ]
        },
        'shipper_accounts':[
            {
                'id': '00000000-0000-0000-0000-000000000000'
            }
        ],
        'is_document': False
    }
    result = rates.calculate(query)

List all rates

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION')
    result = rates.list_all()

Retrieve a rate

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION')
    result = rates.retrieve('RATE_ID')


Labels
------

Crate a label

.. code-block:: python

    from postmen import Labels
    labels = Labels('API_KEY', 'REGION')
    parcel = {
        'box_type': 'custom',
        'dimension': {
            'depth': 40,
            'height': 30,
            'unit': u'cm',
            'width': 20
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
        ],
        'weight': {
            'unit': u'kg',
            'value': 1.5
        }
    }
    sender = {
        'city': 'Grove',
        'company_name': 'Nottingham Inc.',
        'contact_name': 'Nottingham Inc.',
        'country': 'USA',
        'email': 'test@test.com',
        'phone': '1-403-504-5496',
        'postal_code': '74344',
        'state': 'OK',
        'street1': '2511 S. Main St.',
        'type': 'business'
    }
    receiver = {
        'city': 'Medicine Hat',
        'contact_name': 'Rick McLeod (RM Consulting)',
        'country': 'CAN',
        'email': 'test@test.test',
        'phone': '1-403-504-5496',
        'postal_code': 'T1C1Z9',
        'state': 'Alberta',
        'street1': '71 Terrace Crescent NE',
        'street2': 'This is the second streeet',
        'type': 'residential'
    }
    shipment = {
        'async': False,
        'customs': {
            'billing': {
                'method': {
                    'account_number': '950000002',
                    'type': 'account'
                },
                'paid_by': 'shipper'
            },
            'purpose': 'gift'
        },
        'is_document': False,
        'paper_size': 'default',
        'return_shipment': False,
        'service_type': 'dhl_express_0900',
        'shipment': {
            'parcels': [
                parcel
            ],
            'ship_from': sender,
            'ship_to': receiver
        },
        'shipper_account': {
            'id': '00000000-0000-0000-0000-000000000000'
        }
    }
    result = labels.create(shipment)

List all labels

.. code-block:: python

    from postmen import Labels
    labels = Labels('API_KEY', 'REGION')
    result = labels.list_all()

Retrieve a label

.. code-block:: python

    from postmen import Labels
    labels = Labels('API_KEY', 'REGION')
    result = labels.retrieve('LABEL_ID')

Manifests
---------

Create a manifest

List all manifests

.. code-block:: python

    from postmen import Manifests
    manifests = Manifests('API_KEY', 'REGION')
    result = manifests.list_all()

Retrieve a manifest

.. code-block:: python

    from postmen import Manifests
    manifests = Manifests('API_KEY', 'REGION')
    result = manifests.retrieve('MANIFEST_ID')


Cancel Labels
-------------

Cancel a label

List all cancel labels

.. code-block:: python

    from postmen import CancelLabels
    cancel_labels = CancelLabels('API_KEY', 'REGION')
    result = cancel_labels.list_all()

Retrieve a cancel label

.. code-block:: python

    from postmen import CancelLabels
    cancel_labels = CancelLabels('API_KEY', 'REGION')
    result = cancel_labels.retrieve('CANCEL_LABEL_ID')

Additional options
------------------

Custom endpoint

.. code-block:: python

    from postmen import Rates
    host = 'https://api.examples.com'
    rates = Rates('API_KEY', 'REGION', endpoint = host)
    result = rates.retrieve('RATE_ID')

Proxy

.. code-block:: python

    from postmen import Rates
    proxy_server = 'https://username:password@hostname:post'
    rates = Rates('API_KEY', 'REGION', proxy = proxy_server)
    result = rates.retrieve('RATE_ID')

Safe mode

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION', safe = True)
    result = rates.retrieve('RATE_ID')
    if result == None :
        print rates.getError()

Raw JSON response

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION', raw = True)
    raw_json = rates.retrieve('RATE_ID')

Auto retry on number of API calls exceeded.
This SDK in such case by default automatically waits until next call will be possible. If you prefer to raise an exception instead follow this example.

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION', rate = False)
    result = rates.retrieve('RATE_ID')

Automatically retry if exception is retryable.

.. code-block:: python

    from postmen import Rates
    rates = Rates('API_KEY', 'REGION', retry = True)
    result = rates.retrieve('RATE_ID')
