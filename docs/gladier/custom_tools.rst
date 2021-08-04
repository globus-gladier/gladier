Writing Custom Tools
====================

Gladier was designed with the intention that users would write their own tools
as needed. As your pipeline grows, you may include a mix of built-in Gladier
Tools, your own custom tools, or even your own custom package of tools.

Starting with the simple tool below:

.. literalinclude:: example_tool.py
   :language: python

In the same module, this can be added to a client by simply adding the ``MakeDirs``
class to ``gladier_tools``:


.. code-block::

   # from gladier import GladierBaseClient
   @generate_flow_definition
   class ExampleClient(GladierBaseClient):
      gladier_tools = [MakeDirs]

Import strings are an optional feature of Gladier. They're used for built-in tools
to keep a mental boundary from code executing remotely via FuncX Functions. You can
create your own repository of tools and share it provided your tools are organized
within a python package. See the Gladier Tools repository as an example.