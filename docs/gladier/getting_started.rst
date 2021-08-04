Getting Started
===============

The guide here shows a step by step guide to archiving a file and transferring it.
Provided you have done the :ref:`setup`, you can run this full example in
the Tar and Transfer section in :ref:`examples`.

A typical Gladier Client looks like the following:

.. literalinclude:: ../examples/tar_and_transfer.py
   :language: python
   :pyobject: TarAndTransfer


The new class has two main attributes:

* ``gladier_tools`` -- Defines which tools you want to use for this client
* ``@generate_flow_definition`` -- Splices together flows on each tool into one single runnable flow

Each Gladier tool sets its own FuncX Functions, required input, and separate Globus Flow. The
Gladier Client gathers everything into one place. It handles registering functions, ensuring each
tools input requirements are met, and deploying/updating the final combined Globus flow. After that,
running the flow is as simple as these two lines:


.. code-block:: python

   tar_transfer_cli = TarAndTransfer()
   flow = tar_transfer_cli.run_flow()

The first line instantiates the client with default values, which means it will automatically
trigger login for Globus Auth and register Flows and FuncX functions as needed.

The second line, ``flow = hello_cli.run_flow()``, is responsible for several different
things:

* Gathering default input from each tool
* Validating input for each tool
* Triggering an initial login for access to FuncX and the Flows Service
* Registering funcx functions (And re-registering, if they have changed)
* Registering the ``flow_definition`` (And updating if it has changed)
* Triggering a second login to authorize the deployed flow
* Starting the flow

Once this checklist is complete, the flow is stared and will run through each
flow-state in sequence. First, taring a directory then transferring the resulting
archive. Nothing more is needed from Gladier, however there are extra tools for
tracking a flows progress and output.


.. code-block:: python

  tar_transfer_cli.progress(flow['action_id'])
  details = tar_transfer_cli.get_status(flow['action_id'])
  pprint(details)

``hello_cli.progress()`` will periodically query the status of the flow until it finishes. It's
a nice way to watch progression as the flow executes. Once the flow has finished,
``hello_cli.get_status()`` will fetch output from the Globus Flow, so it can be displayed in a
readable format.

Re-Running Flows
----------------

The most useful aspects of Gladier come into play when making changes to a flow
or function. Both Flows and Functions are checksummed on each run to detect changes,
and Gladier will automatically re-register any function that has changed, or update
the flow if it has changed. This allows users to focus on writing functions without
worrying if a change has been applied. Entire tools can also be added or removed from
a flow simply by commenting them out.

Each flow or function update is logged in the ``INFO`` log in python. Additionally,
if you wish to see the full flow definition at any time, it can be queried in an
instantiated client like so:

.. code-block:: python

  tar_transfer_cli = TarAndTransfer()
  pprint(tar_transfer_cli.flow_definition)

Next Steps
----------

Running examples in the :ref:`examples` section is highly recommended.