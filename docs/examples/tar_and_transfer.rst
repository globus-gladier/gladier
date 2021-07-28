Tar and Transfer
----------------

This example highlights the usage of the Tar and Transfer Gladier tools in a single flow.

.. literalinclude:: tandt.py
   :language: python


Steps
-----

Start the workflow by overriding the Gladier Client with a list of the
tools you want to use. In this case, we want to use the Tar, and Transfer tools.


.. code-block:: python

   @generate_flow_definition
   class TarAndTransfer(GladierBaseClient):
       gladier_tools = [
       'gladier_tools.posix.Tar',
       'gladier_tools.globus.Transfer',
        ]
    
The ``@generate_flow_definition`` decorator takes the flow definitions of the individual tools and constructs a flow definition for the new flow, so we do not have 
to define a custom flow definition. To view the constructed flow definition, use ``pprint(tat.flow_definition)``. Refer to the `Flow Generation <https://gladier.readthedocs.io/en/docs/flow_generation.html>`_ doc for more details on the same.

The next step is to define the input for the flow. It might be helpful to refer to the docs for each of the tools to find out what needs to be passed in as input. 
For example, here are the documentations for the `Tar <https://gladier.readthedocs.io/en/docs/tools/posix/tar.html>`_ and `Transfer <https://gladier.readthedocs.io/en/docs/tools/globus/transfer.html>`_ tools. Feel free to use the below blueprint:

.. code-block:: python
    
   flow_input = {
    'input': {
        # Set this to the file/folder that has to be tarred 
        'tar_input': '',
        # Set this to your own funcx endpoint where you want to tar files
        'funcx_endpoint_compute': '',
        # Set this to the globus endpoint where your tarred archive has been created
        'transfer_source_endpoint_id': '',
        # By default, this will transfer the tar file to Globus Tutorial Endpoint 1
        'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
        # Provide the paths to the tarred file as input for the transfer step
        'transfer_source_path': '',
        'transfer_destination_path': '',
        'transfer_recursive': False,
      }
    }

All that is left is to create an instance of the ``GladierBaseClient`` class and run the flow. Use the below code to view the progress of the flow:

.. code-block:: python
    
   tat = TarAndTransfer()
   pprint(tat.flow_definition)
   flow = tat.run_flow(flow_input=flow_input)
   action_id = flow['action_id']
   tat.progress(action_id)
   pprint(tat.get_status(action_id))
