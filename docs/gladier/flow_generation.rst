.. _flow_generation:

Flow Generation
===============

For simple flows, Gladier can handle the process of stitching together the flows of
several tools into one big flow, or even generating a flow from scratch for a simple
Gladier tool. Flow generation does not replace manually authored flows, but provides
a path for automating simple flows that don't require a lot of branching.

Flow generation is available for both clients and tools with the ``@generate_flow_definition``
decorator. Although it's applied the same way, the decorator behaves a little differently
for a client and a tool.

* Gladier Tool -- Generates a flow for each function defined in ``compute_functions``
* Gladier Client -- Combines flows for each Gladier Tool defined in ``gladier_tools``

Flow Generation on Gladier Tools
--------------------------------

For Gladier Tools that only need one flow step per Compute Function, flow generation
can be a good option. Gladier will automatically determine information about the functions
on the tool, and incorporate them into the flow. The usage looks like this:


.. literalinclude:: flow_generation/fs_list_example.py
   :language: python

The decorator ``@generate_flow_definition`` will automatically set the ``flow_definition``
attribute when a GladierClient includes it in ``tools``. The flow it generates will be
identical to the following:

.. literalinclude:: flow_generation/fs_list_flow.json
   :language: json


Flow Generation Modifiers
^^^^^^^^^^^^^^^^^^^^^^^^^

You'll notice that flow generation makes some assumptions you might want to change. For
example, ``ls`` is not a compute heavy task, and might be better to run on the head node.
Overriding some attributes of the flow can be done with ``modifiers``.


.. code-block::

    @generate_flow_definition(modifiers={
        ls: {'endpoint': 'compute_endpoint'}
    })
    class FileSystemListCommand(GladierBaseTool):
        """List files on the filesystem"""
        compute_functions = [ls]



Flow Generation on Gladier Clients
----------------------------------

When Flow Generation is applied to Gladier Clients it does not generate the flow
from scratch, but instead combines the flow on each Gladier Tool into one big flow.

Note that modifiers can also be used with Gladier Clients to customize some attributes.


.. code-block::

    @generate_flow_definition(modifiers={
       'generate_metadata': {'endpoint': 'compute_endpoint'},
       'publish_to_search': {'endpoint': 'compute_endpoint',
                             'payload': 'generate_metadata'}
    })
    class ProcessData(GladierBaseClient):
        gladier_tools = [
            'mytools.TransferData',
            'mytools.processing.ProcessData',
            'mytools.processing.GenerateGraphs',
            'mytools.processing.GenerateMetadata',
            'mytools.processing.PublishResults',
        ]

Modifiers
^^^^^^^^^

A complete reference is coming soon!
