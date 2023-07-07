Encrypt and Transfer
====================

This example highlights the usage of built in tools (Tar, Encrypt and Transfer) along with a custom defined tool (MakeFiles) in the same flow.

.. literalinclude:: encrypt_and_transfer.py
   :language: python


Steps
-----
We start by writing our own custom tool. For the example, MakeFiles is a trivial tool that creates three files in a given folder.
The comptue function that achieves this functionality is ``make_files``. We then define the tool using ``GladierBaseTool``. 


.. code-block:: python
    
    @generate_flow_definition
    class MakeFiles(GladierBaseTool):
        compute_functions = [make_files]
        required_input = [
            'make_input',
            'compute_endpoint'
        ]

Defining a workflow is similar to the previous case, where we override the ``GladierBaseClient`` class. In this case, we want to use the MakeFiles, Tar, Encrypt, and Transfer tools.


.. code-block:: python

    @generate_flow_definition
    class CustomTransfer(GladierBaseClient):
        gladier_tools = [
            MakeFiles,
            'gladier_tools.posix.Tar',
            'gladier_tools.posix.Encrypt',
            'gladier_tools.globus.Transfer',
        ]
    
The ``@generate_flow_definition`` decorator takes the flow definitions of the individual tools and constructs a flow definition for the new flow, so we do not have 
to define a custom flow definition. To view the constructed flow definition, use ``pprint(ct.flow_definition)``. Refer to the `Flow Generation <https://gladier.readthedocs.io/en/docs/flow_generation.html>`_ doc for more details on the same.

The next step is to define the input for the flow. It might be helpful to refer to the docs for each of the tools to find out what needs to be passed in as input. 
For example, here are the documentations for the `Tar <https://gladier.readthedocs.io/en/docs/tools/posix/tar.html>`_, `Encrypt <https://gladier.readthedocs.io/en/docs/tools/posix/encrypt.html>`_ and `Transfer <https://gladier.readthedocs.io/en/docs/tools/globus/transfer.html>`_ tools. Feel free to use the below blueprint:

.. code-block:: python
    
    flow_input = {
        'input': {
            # Set this to the folder in which you want to run the makeFiles function in
            'make_input': '',
            # Set this to the same folder as above
            'tar_input': '',
            # Set this to the resultant archive of the above folder
            'encrypt_input': '',
            # Set this to the symmetric key you want to use to encrypt/decrypt the file
            'encrypt_key': '',
            # Set this to your own compute endpoint where you want to encrypt files
            'compute_endpoint': '',
            # Set this to the globus endpoint where your encrypted archive has been created
            'transfer_source_endpoint_id': '',
            # By default, this will transfer the encrypt file to Globus Tutorial Endpoint 1
            'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
            'transfer_source_path': '',
            'transfer_destination_path': '',
            'transfer_recursive': False,
        }
    }

All that is left is to create an instance of the ``GladierBaseClient`` class and run the flow. Use the below code to view the progress of the flow:

.. code-block:: python
    
    ct = CustomTransfer()
    pprint(ct.flow_definition)
    flow = ct.run_flow(flow_input=flow_input)
    action_id = flow['action_id']
    ct.progress(action_id)
    pprint(ct.get_status(action_id))
