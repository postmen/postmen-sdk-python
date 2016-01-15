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

Labels
------

Crate a label

List all labels

.. code-block:: python

    from postmen import Labels
    labels = Labels('API_KEY', 'REGION')
    result = labels.list_all()

Retrieve a label

Manifests
---------

Create a manifest

List all manifests

.. code-block:: python

    from postmen import Manifests
    manifests = Manifests('API_KEY', 'REGION')
    result = manifests.list_all()

Retrieve a manifest

Cancel Labels
-------------

Cancel a label

List all cancel labels

.. code-block:: python

    from postmen import CancelLabels
    cancel_labels = CancelLabels('API_KEY', 'REGION')
    result = cancel_labels.list_all()

Retrieve a cancel label
