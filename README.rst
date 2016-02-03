Introduction
------------

PHP SDK for `Postmen API <https://docs.postmen.com/>`__. For problems
and suggestions please open `GitHub
issue <https://github.com/postmen/postmen-sdk-php/issues>`__

**Table of Contents**

-  `Installation <#installation>`__
-  `Quick Start <#quick-start>`__
-  `class Postmen <#class-postmen>`__

   -  `Postmen(api\_key, region,
      \*\*kwargs) <#postmenapi_key-region-config--array>`__
   -  `create(self, resource, payload,
      \*\*kwargs) <#createresource-payload-config--array>`__
   -  `get(self, resource, id\_=None,
      \*\*kwargs) <#getresource-id--null-query--array-config--array>`__
   -  `getError() <#geterror>`__
   -  `GET(self, path,
      \*\*kwargs) <#callgetpath-query--array-options--array>`__
   -  `POST(self, path,
      \*\*kwargs) <#callpostpath--array-options--array>`__
   -  `PUT(self, path,
      \*\*kwargs) <#callputpath--array-options--array>`__
   -  `DELETE(self, path,
      \*\*kwargs) <#calldeletepath--array-options--array>`__

-  `Error Handling <#error-handling>`__

   -  `class PostmenException <#class-postmenexception>`__
   -  `Automatic retry on retryable
      error <#automatic-retry-on-retryable-error>`__

-  `Examples <#examples>`__

   -  `Full list <#full-list>`__
   -  `How to run <#how-to-run>`__
   -  `Navigation table <#navigation-table>`__

-  `Testing <#testing>`__
-  `License <#license>`__
-  `Contributors <#contributors>`__

Installation
------------

Manual
^^^^^^

Download or clone this repo, then run

``python setup.py install``

PyPI
^^^^

Run ``pip install postmen``

Quick Start
-----------

In order to get API key and choose a region refer to the
`documentation <https://docs.postmen.com/overview.html>`__.

.. code:: python

    import pprint

    pp = pprint.PrettyPrinter(indent=4)

    from postmen import Postmen

    api_key = 'YOUR_API_KEY'
    region = 'sandbox'

    # create Postmen API handler object

    api = Postmen(api_key, region)

    try:
        # as an example we request all the labels
        
        result = api.get('labels')
        print "RESULT:"
        pp.pprint(result)
    except PostmenException as e:
        // if error occurs we can access all
        // the details in following way
        
        print "ERROR";
        print e.code()  // error code
        print e.message() // error message
        pp.pprint(e.details())  // details

class Postmen
-------------

Postmen(api\_key, region, \*\*kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Initiate Postmen SDK object. In order to get API key and choose a region
refer to the `documentation <https://docs.postmen.com/overview.html>`__.

+------------------+---------------------+------+-------+---------------------------+
| Argument         | Required            | Type | Defau | Description               |
|                  |                     |      | lt    |                           |
+==================+=====================+======+=======+===========================+
| ``api_key``      | YES                 | Stri | N / A | API key                   |
|                  |                     | ng   |       |                           |
+------------------+---------------------+------+-------+---------------------------+
| ``region``       | NO if ``endpoint``  | Stri | N / A | API region (``sandbox``,  |
|                  | is set              | ng   |       | ``production``)           |
+------------------+---------------------+------+-------+---------------------------+
| ``endpoint``     | —                   | Stri | N / A | Custom URL API endpoint   |
|                  |                     | ng   |       |                           |
+------------------+---------------------+------+-------+---------------------------+
| ``retry``        | —                   | Bool | ``TRU | Automatic retry on        |
|                  |                     | ean  | E``   | retryable errors          |
+------------------+---------------------+------+-------+---------------------------+
| ``rate``         | —                   | Bool | ``TRU | Wait before API call if   |
|                  |                     | ean  | E``   | rate limit exceeded or    |
|                  |                     |      |       | retry on 429 error        |
+------------------+---------------------+------+-------+---------------------------+
| ``safe``         | —                   | Bool | ``FAL | Suppress exceptions on    |
|                  |                     | ean  | SE``  | errors, None would be     |
|                  |                     |      |       | returned instead, check   |
|                  |                     |      |       | `Error                    |
|                  |                     |      |       | Handling <#error-handling |
|                  |                     |      |       | >`__                      |
+------------------+---------------------+------+-------+---------------------------+
| ``raw``          | —                   | Bool | ``FAL | To return API response as |
|                  |                     | ean  | SE``  | a raw string              |
+------------------+---------------------+------+-------+---------------------------+
| ``proxy``        | —                   | Dict | ``{}` | Proxy credentials,        |
|                  |                     | iona | `     | handled as in `requests   |
|                  |                     | ry   |       | library <http://docs.pyth |
|                  |                     |      |       | on-requests.org/en/latest |
|                  |                     |      |       | /user/advanced/#proxies>` |
|                  |                     |      |       | __                        |
+------------------+---------------------+------+-------+---------------------------+
| ``time``         | —                   | Bool | ``Fal | Convert ISO time strings  |
|                  |                     | ean  | se``  | into                      |
|                  |                     |      |       | `datetime <https://docs.p |
|                  |                     |      |       | ython.org/2/library/datet |
|                  |                     |      |       | ime.html#datetime-objects |
|                  |                     |      |       | >`__                      |
|                  |                     |      |       | objects                   |
+------------------+---------------------+------+-------+---------------------------+

create(self, resource, payload, \*\*kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creates API ``resource`` object, returns new object payload as
``Dictionary``.

+-----------+---------+-------------+---------+--------------------------------------+
| Argument  | Require | Type        | Default | Description                          |
|           | d       |             |         |                                      |
+===========+=========+=============+=========+======================================+
| ``resourc | YES     | String      | N / A   | Postmen API resourse ('rates',       |
| e``       |         |             |         | 'labels', 'manifests')               |
+-----------+---------+-------------+---------+--------------------------------------+
| ``payload | YES     | Array or    | N / A   | Payload according to API             |
| ``        |         | String      |         |                                      |
+-----------+---------+-------------+---------+--------------------------------------+
| ``**kwarg | NO      | Named       | N / A   | Override constructor                 |
| s``       |         | arguments   |         | `config <#postmenapi_key-region-conf |
|           |         |             |         | ig--array>`__                        |
+-----------+---------+-------------+---------+--------------------------------------+

**API Docs:** - `POST
/rates <https://docs.postmen.com/#rates-calculate-rates>`__ - `POST
/labels <https://docs.postmen.com/#labels-create-a-label>`__ - `POST
/manifests <https://docs.postmen.com/#manifests-create-a-manifest>`__ -
`POST
/cancel-labels <https://docs.postmen.com/#cancel-labels-cancel-a-label>`__

**Examples:** -
`rates\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_create.py>`__
-
`labels\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_create.py>`__
-
`manifests\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_create.py>`__
-
`cancel\_labels\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_create.py>`__

get(self, resource, id\_=None, \*\*kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Gets API ``$resource`` objects (list or a single objects).

+-----------+---------+-------------+---------+--------------------------------------+
| Argument  | Require | Type        | Default | Description                          |
|           | d       |             |         |                                      |
+===========+=========+=============+=========+======================================+
| ``resourc | YES     | String      | N / A   | Postmen API resourse ('rates',       |
| e``       |         |             |         | 'labels', 'manifests')               |
+-----------+---------+-------------+---------+--------------------------------------+
| ``id``    | NO      | String      | ``None` | Object ID, if not set 'list all' API |
|           |         |             | `       | method is used                       |
+-----------+---------+-------------+---------+--------------------------------------+
| ``**kwarg | NO      | Named       | N / A   | ``query``, and other values          |
| s``       |         | arguments   |         | overriding constructor               |
|           |         |             |         | `config <#postmenapi_key-region-conf |
|           |         |             |         | ig--array>`__                        |
+-----------+---------+-------------+---------+--------------------------------------+

**API Docs:** - `GET
/rates <https://docs.postmen.com/#rates-list-all-rates>`__ - `GET
/rates/:id <https://docs.postmen.com/#rates-retrieve-rates>`__ - `GET
/labels <https://docs.postmen.com/#labels-list-all-labels>`__ - `GET
/labels/:id <https://docs.postmen.com/#labels-retrieve-a-label>`__ -
`GET
/manifests <https://docs.postmen.com/#manifests-list-all-manifests>`__ -
`GET
/manifests/:id <https://docs.postmen.com/#manifests-retrieve-a-manifest>`__
- `GET
/cancel-labels <https://docs.postmen.com/#cancel-labels-list-all-cancel-labels>`__
- `GET
/cancel-labels/:id <https://docs.postmen.com/#cancel-labels-retrieve-a-cancel-label>`__

**Examples:** -
`rates\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_retrieve.py>`__
-
`labels\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_retrieve.py>`__
-
`manifests\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_retrieve.py>`__
-
`cancel\_labels\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_retrieve.py>`__

getError()
^^^^^^^^^^

Returns SDK error, `PostmenException type <#class-postmenexception>`__
if named argument ``safe = True`` was set.

Check `Error Handling <#error-handling>`__ for details.

GET(self, path, \*\*kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Performs HTTP GET request, returns an ``Dictionary`` object holding API
response.

+-----------+---------+----------------+---------+-----------------------------------+
| Argument  | Require | Type           | Default | Description                       |
|           | d       |                |         |                                   |
+===========+=========+================+=========+===================================+
| ``path``  | YES     | String         | N / A   | URL path (e.g. 'v3/labels' for    |
|           |         |                |         | ``https://sandbox-api.postmen.com |
|           |         |                |         | /v3/labels``                      |
|           |         |                |         | )                                 |
+-----------+---------+----------------+---------+-----------------------------------+
| ``**kwarg | NO      | Named          | ``array | ``query``, and other values       |
| s``       |         | arguments      | ()``    | overriding constructor            |
|           |         |                |         | `config <#postmenapi_key-region-c |
|           |         |                |         | onfig--array>`__                  |
+-----------+---------+----------------+---------+-----------------------------------+

POST(self, path, **kwargs) #### PUT(self, path, **\ kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DELETE(self, path, \*\*kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Performs HTTP POST/PUT/DELETE request, returns a ``Dictionary`` object
holding API response.

+-----------+---------+----------------+---------+-----------------------------------+
| Argument  | Require | Type           | Default | Description                       |
|           | d       |                |         |                                   |
+===========+=========+================+=========+===================================+
| ``path``  | YES     | String         | N / A   | URL path (e.g. 'v3/labels' for    |
|           |         |                |         | ``https://sandbox-api.postmen.com |
|           |         |                |         | /v3/labels``                      |
|           |         |                |         | )                                 |
+-----------+---------+----------------+---------+-----------------------------------+
| ``body``  | YES     | Dictionary or  | N / A   | HTTP POST/PUT/DELETE request body |
|           |         | String         |         |                                   |
+-----------+---------+----------------+---------+-----------------------------------+
| ``**kwarg | NO      | Named          | N / A   | Override constructor              |
| s``       |         | arguments      |         | `config <#postmenapi_key-region-c |
|           |         |                |         | onfig--array>`__                  |
+-----------+---------+----------------+---------+-----------------------------------+

Error Handling
--------------

Particular error details are listed in the
`documentation <https://docs.postmen.com/errors.html>`__.

All SDK methods may throw an exception described below.

class PostmenException
^^^^^^^^^^^^^^^^^^^^^^

+------------+-----------+------------------------------------------------------+
| Method     | Return    | Description                                          |
|            | type      |                                                      |
+============+===========+======================================================+
| code()     | Integer   | Error code                                           |
+------------+-----------+------------------------------------------------------+
| retryable( | Boolean   | Indicates if error is retryable                      |
| )          |           |                                                      |
+------------+-----------+------------------------------------------------------+
| message()  | String    | Error message (e.g.                                  |
|            |           | ``The request was invalid or cannot be otherwise ser |
|            |           | ved``)                                               |
+------------+-----------+------------------------------------------------------+
| details()  | List      | Error details (e.g.                                  |
|            |           | ``Destination country must be RUS or KAZ``)          |
+------------+-----------+------------------------------------------------------+

In case of ``safe = True`` SDK would not throw exceptions,
`getError() <#geterror>`__ must be used instead.

Example:
`error.php <https://github.com/postmen/postmen-sdk-php/blob/master/examples/error.php>`__

Automatic retry on retryable error
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If API error is retryable, SDK will wait for delay and retry. Delay
starts from 1 second. After each try, delay time is doubled. Maximum
number of attempts is 5.

To disable this option set ``retry = False``

Examples
--------

Full list
^^^^^^^^^

All examples avalible listed in the table below.

+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| File                                                                                                                             | Description                            |
+==================================================================================================================================+========================================+
| `rates\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_create.py>`__                        | ``rates`` object creation              |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `rates\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_retrieve.py>`__                    | ``rates`` object(s) retrieve           |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `labels\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_create.py>`__                      | ``labels`` object creation             |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `labels\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_retrieve.py>`__                  | ``labels`` object(s) retrieve          |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `manifests\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_create.py>`__                | ``manifests`` object creation          |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `manifests\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_retrieve.py>`__            | ``manifests`` object(s) retrieve       |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `cancel\_labels\_create.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_create.py>`__       | ``cancel-labels`` object creation      |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `cancel\_labels\_retrieve.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_retrieve.py>`__   | ``cancel-labels`` object(s) retrieve   |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `proxy.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/proxy.py>`__                                       | Proxy usage                            |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+
| `error.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/error.py>`__                                       | Avalible ways to catch/get errors      |
+----------------------------------------------------------------------------------------------------------------------------------+----------------------------------------+

How to run
^^^^^^^^^^

Download the source code, go to ``examples`` directory.

If you already installed Postmen SDK for Python you can proceed,
otherwise install it by running ``python setup.py install`` or using
PyPI.

Put your API key and region to
`credentials.py <https://github.com/postmen/postmen-sdk-python/blob/master/examples/credentials.py>`__

Check the file you want to run before run. Some require you to set
additional variables.

Navigation table
^^^^^^^^^^^^^^^^

For each API method SDK provides Python wrapper. Use the table below to
find SDK method and example that match your need.

.. raw:: html

   <table>

.. raw:: html

   <tr>

::

    <th>Model \ Action</th>
    <th>create</th>
    <th>get all</th>
    <th>get by id</th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <th>rates</th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_create.py">
      <code>.create('rates', payload)</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_retrieve.py#L16">
      <code>.get('rates')</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/rates_retrieve.py#L18">
      <code>.get('rates', id)</code>
    </a></sub></th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <th>labels</th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_create.py">
      <code>.create('labels', payload)</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_retrieve.py#L16">
      <code>.get('labels')</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/labels_retrieve.py#L18">
      <code>.get('labels', id)</code>
    </a></sub></th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <th>manifest</th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_create.py">
      <code>.create('manifest', payload)</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_retrieve.py#L16">
      <code>.get('manifest')</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/manifests_retrieve.py#L18">
      <code>.get('manifest', id)</code>
    </a></sub></th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <th>cancel-labels</th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_create.py">
      <code>.create('cancel-labels', payload)</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_retrieve.py#L16">
      <code>.get('cancel-labels')</code>
    </a></sub></th>
    <th><sub><a href="https://github.com/postmen/postmen-sdk-python/blob/master/examples/cancel_labels_retrieve.py#L18">
      <code>.get('cancel-labels', id)</code>
    </a></sub></th>

.. raw:: html

   </tr>

.. raw:: html

   </table>

Testing
-------

If you contribute to SDK, run automated test before you make pull
request.

``python setup.py test``

License
-------

Released under the MIT license. See the LICENSE file for details.

Contributors
------------

-  Fedor Korshunov - `view
   contributions <https://github.com/postmen/sdk-python/commits?author=fedor>`__
-  Marek Narozniak - `view
   contributions <https://github.com/postmen/sdk-python/commits?author=marekyggdrasil>`__
