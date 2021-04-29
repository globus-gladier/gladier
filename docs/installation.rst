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

With Gladier Installed, you can now put together some basic clients!
Setup your workflow by overriding the Gladier Client with a list of the
tools you want to use. An example looks like this:

.. literalinclude:: tools/gladier_example.py
   :language: python
   :pyobject: HelloGladier


The new class has two main attributes:

* ``gladier_tools`` -- Defines which tools you want to use for this client
* ``flow_definition`` -- Defines how automate will run your tools

You may notice that both have similar values, ``gladier.tools.hello_world.HelloWorld``.
Each Gladier tool comes with its own built-in flow so it can easily be tested separately.
Gladier Tools also contain their own ``required_input``, default ``flow_input``, and
defined ``funcx_functions``.

More on these components later. For now, let's run the flow!

.. code-block:: python

   hello_cli = HelloGladier()
   flow = hello_cli.start_flow()

The first line instantiates the client with default values, which means it will automatically
trigger login for Globus Auth and register Flows and FuncX functions as needed, without asking.

The second line, ``flow = hello_cli.start_flow()``, iterates over all defined tools and starts the flow. A bunch of things happen
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

``progress()`` will periodically query the status of the flow until it finishes. It's
a nice way to watch progression as the flow executes. Once the flow has finished,
``get_details()`` will fetch output from the Globus Flow, so it can be displayed in a
readable format.
Running A Gladier Tool
----------------------

A full code snippet for running everything above is here:

.. literalinclude:: tools/gladier_example.py
   :language: python
