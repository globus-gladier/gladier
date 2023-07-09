Running Flows
=============

We provide a step-by-step guide to creating and running a simple two-step flow that:

1. runs a program on a directory (specifically, Tar, to create an archive file) and
2. transfers the transformed file to another computer.

Provided you have already performed the :ref:`setup`, you can run this full example
in the Tar and Transfer section in :ref:`examples`.
The following code, which implements the Gladier Client for this example, is a
typical Gladier Flow definition.

.. literalinclude:: ../examples/tar_and_transfer.py
   :language: python
   :pyobject: TarAndTransfer


The new class has two main attributes:

* ``gladier_tools`` -- Defines the tools that are to be used this client -- in this case, the
  ``gladier_tools.posix.Tar`` and ``gladier_tools.globus.Transfer`` tools defined in Examples
* ``@generate_flow_definition`` -- Splices together flows on each tool into one single runnable flow

Each Gladier tool sets its own Compute Functions, required input, and separate Globus Flow. The
Gladier Client gathers everything into one place. It handles registering functions, ensuring each
tools input requirements are met, and deploying/updating the final combined Globus flow. After that,
running the flow is as simple as these two lines:


.. code-block:: python

   tar_transfer_cli = TarAndTransfer()
   flow = tar_transfer_cli.run_flow()

The first line instantiates the client with default values, which means that it will automatically
trigger a Globus Auth login and register Flows and Compute Functions as needed.

The second line, ``flow = hello_cli.run_flow()``, is responsible for the following things

* Gather default input from each tool
* Validate input for each tool
* Trigger an initial login for access to the Compute Service and the Flows Service
* Register Compute Functions (and re-register them, if they were previously registered and have changed)
* Register the flow_definition (and update it, if it was previously registered, and has changed)
* Trigger a second login to authorize the deployed flow
* Start the flow

Once these steps have been performed, the flow is started and will perform the two steps one after
the other: 1) tar a directory and 2) transfer the resulting archive.
Gladier provides tools for tracking a flow's progress and output:

Once this checklist is complete, the flow is stared and will run through each
flow-state in sequence. First, taring a directory then transferring the resulting
archive. Nothing more is needed from Gladier, however there are extra tools for
tracking a flows progress and output.


.. code-block:: python

  tar_transfer_cli.progress(flow['action_id'])
  details = tar_transfer_cli.get_status(flow['action_id'])
  pprint(details)

``hello_cli.progress()`` will periodically query the status of the flow until it finishes.
It's a nice way to watch progression as the flow executes. Once the flow has finished,
``hello_cli.get_status()`` will fetch output from the Globus Flow, so it can be displayed
in a readable format.

Re-Running Flows
----------------

Gladier makes it easy to change a flow or function. Both Flows and Functions are checksummed
on each run so that changes to either can be detected automatically; Gladier will then
re-register any function that has changed and update the flow if it has changed.
Thus, users can focus on writing functions without worrying if a change has been registered.
New tools can also be added to a flow, and tools can be removed from a flow simply by
commenting them out.

Each flow or function update is logged in the ``INFO`` log in Python. Additionally, if you wish to
see the full flow definition at any time, it can be queried in an instantiated client like so:

.. code-block:: python

  tar_transfer_cli = TarAndTransfer()
  pprint(tar_transfer_cli.flow_definition)

Next Steps
----------

* See the :ref:`examples` section for full code snippets and interactive demos
* See :ref:`gladier_tools_package` for a list of pre-made tools
* :ref:`tools` for creating your own tools
* :ref:`sdk_reference` for detailed information about Gladier SDK components
