Encrypt and Transfer
====================

This example highlights the usage of the Encrypt and Transfer Gladier tools in a single flow. The encrypt step creates a file encrypting the original contents using AES-128 bit encryption, and the transfer step transfers the archived file between Globus Endpoints.

.. literalinclude:: eandt.py
   :language: python


Steps
-----

Start the workflow by overriding the Gladier Client with a list of the
tools you want to use. In this case, we want to use the Encrypt, and Transfer tools.


.. code-block:: python

    @generate_flow_definition
    class EncryptAndTransfer(GladierBaseClient):
        gladier_tools = [
            'gladier_tools.posix.Encrypt',
            'gladier_tools.globus.Transfer',
        ]
    
The ``@generate_flow_definition`` decorator takes the flow definitions of the individual tools and constructs a flow definition for the new flow, so we do not have 
to define a custom flow definition. To view the constructed flow definition, use ``pprint(eat.flow_definition)``. Refer to the `Flow Generation <https://gladier.readthedocs.io/en/docs/flow_generation.html>`_ doc for more details on the same.

The next step is to define the input for the flow. It might be helpful to refer to the docs for each of the tools to find out what needs to be passed in as input. 
For example, here are the documentations for the `Encrypt <https://gladier.readthedocs.io/en/docs/tools/posix/encrypt.html>`_ and `Transfer <https://gladier.readthedocs.io/en/docs/tools/globus/transfer.html>`_ tools. Feel free to use the below blueprint:

.. code-block:: python
    
    flow_input = {
        'input': {
            'encrypt_input': '',
            # Set this to the symmetric key you want to use to encrypt/decrypt the file
            'encrypt_key':'', 
            # Set this to your own funcx endpoint where you want to encrypt files
            'funcx_endpoint_compute': '',
            # Set this to the globus endpoint where your encrypted file has been created
            'transfer_source_endpoint_id': '',
            # By default, this will transfer the encrypted file to Globus Tutorial Endpoint 1
            'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
            'transfer_source_path': '',
            'transfer_destination_path': '',
            'transfer_recursive': False,
        }
    }

All that is left is to create an instance of the ``GladierBaseClient`` class and run the flow. Use the below code to view the progress of the flow:

.. code-block:: python
    
    eat = EncryptAndTransfer()
    pprint(eat.flow_definition)
    flow = eat.run_flow(flow_input=flow_input)
    action_id = flow['action_id']
    eat.progress(action_id)
    pprint(eat.get_status(action_id))
