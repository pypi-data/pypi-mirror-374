
Installation
===========

You can install apikit using pip:

.. code-block:: bash

   pip install apikit

For development installation:

.. code-block:: bash

   pip install -e ".[dev]"

Usage
=====

Basic usage example:

.. code-block:: python

   from apikit import APIClient

   # Create a client
   client = APIClient(base_url="https://api.example.com")

