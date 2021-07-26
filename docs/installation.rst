Installation
============

Gladier requires Python 3.6 and higher. For a modern version of python,
see the official `Python Installation Guide <https://docs.python-guide.org/starting/installation/>`_.

The easiest way to get Gladier is through Pip on PyPi. Gladier is built with two
main packages, the core Gladier client and Gladier Tools. Gladier Tools include
a set of reusable, common operations. Installing it is highly recommended.

With pip installed, you can do the following:


.. code-block:: bash

   pip install gladier gladier-tools

Getting Started
===============

.. note::
   Below requires setting up your own **FuncX Endpoint**. If you only want to run
   Gladier Examples without setting up your own endpoints, we recommend
   `The Binder Notebook Examples <https://github.com/globus-gladier/gladier-examples>`_.


Before you run your first Gladier Client, you need to setup your Funcx Endpoint. The
`First Time Setup Guide <https://funcx.readthedocs.io/en/latest/endpoints.html#first-time-setup>`_
in the FuncX docs covers this well. After that, you can run the example below:

.. literalinclude:: tools/gladier_example.py
   :language: python
   :pyobject: HelloGladier


The new class has two main attributes:

* ``gladier_tools`` -- Defines which tools you want to use for this client
* ``flow_definition`` -- Defines the Globus Flow that will run each tool

You may notice that both have similar values, ``gladier.tools.hello_world.HelloWorld``.
Each Gladier tool comes with its own built-in flow so it can easily be tested separately.
Gladier Tools also contain their own ``required_input``, default ``flow_input``, and
defined ``funcx_functions``.

More on these components later. For now, let's run the flow!

.. code-block:: python

   hello_cli = HelloGladier()
   flow = hello_cli.run_flow()

The first line instantiates the client with default values, which means it will automatically
trigger login for Globus Auth and register Flows and FuncX functions as needed, without asking.

The second line, ``flow = hello_cli.run_flow()``, iterates over all defined tools and starts the flow. A bunch of things happen
here, including:

* Gathering input from each tool
* Validating input for each tool
* Triggering a login, if needed
* Registering funcx functions (And re-registering, if they have changed)
* Registering the ``flow_definition`` (And re-registering, if it has changed)
* Starting the flow

Now, the flow will run and complete. This is great, but it would be nice to get more details on
whats happening. The GladierClient comes with some built-in functions to help with this:


.. code-block:: python

  hello_cli.progress(flow['action_id'])
  details = hello_cli.get_details(flow['action_id'], 'HelloFuncXResult')
  pprint(details)

``hello_cli.progress()`` will periodically query the status of the flow until it finishes. It's
a nice way to watch progression as the flow executes. Once the flow has finished,
``hello_cli.get_details()`` will fetch output from the Globus Flow, so it can be displayed in a
readable format.

Running A Gladier Tool
----------------------

A full code snippet for running everything above is here:

.. literalinclude:: tools/gladier_example.py
   :language: python

Remember to replace ``<your_funcx_endpoint>`` with the UUID for your endpoint.
You can use ``funcx-endpoint`` to list the endpoints running on your machine.
If you need to setup a new funcx-endpoint, see the
`FuncX-Endpoint first time setup <https://funcx.readthedocs.io/en/latest/endpoints.html#first-time-setup>`_

Running the code above with a live FuncX endpoint will result in the following:

.. code-block:: bash

  $ python hello_world.py
  Starting login with Globus Auth, press ^C to cancel.
  [ACTIVE]: State HelloFuncX of type Action started
  [ACTIVE]: State HelloFuncX of type Action started
  [ACTIVE]: An Action is running
  [ACTIVE]: An Action is running
  {'action_id': '058b3cf7-f602-4b9c-8b29-661779f7c129',
   'details': {'completion_t': '1623959367.248737',
               'exception': None,
               'result': 'hello world',
               'status': 'SUCCEEDED',
               'task_id': '058b3cf7-f602-4b9c-8b29-661779f7c129'},
   'release_after': 'P30D',
   'state_name': 'HelloFuncX',
   'status': 'SUCCEEDED'}
