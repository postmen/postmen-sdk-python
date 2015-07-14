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
        api = postmen.API('POSTMEN_API_KEY', 'sandbox')
        labels = api.get('labels')
    except PostmenError, e:
        print('Error: %s' % e)
