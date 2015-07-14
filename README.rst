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

Quick Start
-----------

The following code list all labels for API key.

.. code-block:: python

    import postmen
    try:
        api = postmen.API('API_KEY', 'sandbox')
        labels = api.get('labels')
    except PostmenError, e:
        print('Error: %s' % e)

Get API object
--------------

Import postmen module and obtain API object. Pass valid API key and region (sandbox, us-west, ap-southeast).

.. code-block:: python

    import postmen
    api = postmen.API('API_KEY', 'REGION')

Find detailed description in `API class documentation <http://postmen-python-sdk.readthedocs.org/en/latest/postmen.html#postmen.API>`_.

Make API calls
--------------

Common method to make API call (normally you shouldn't use it directly):

#. **.call(method, path, payload)**

HTTP-methods access to directly map API docs to SDK calls:

#. **.GET(path)**
#. **.POST(path, payload)**

User-friendly API access methods:

#. **.get(resource, [id])**: get all resources (e.g. `list all labels <https://docs.postmen.com/#label-list-all-labels>`_) or specific resource if id is specified (e.g. `retrieve a label <https://docs.postmen.com/#label-retrieve-a-label>`_)
#. **.create(resource, payload)**: create a new resource (e.g. `create label <https://docs.postmen.com/#label-create-a-label>`_)
#. **.cancel(resource, id)**: delete/cancel a resource (e.g. `cancel a label <https://docs.postmen.com/#label-cancel-a-label>`_)

**path, resource, id** are strings.

**payload** is JSON string or dict/list.

All methods accept optional arguments for **.call()**. Find detailed description in `API.call() documentation <http://postmen-python-sdk.readthedocs.org/en/latest/postmen.html#postmen.API.call>`_.
