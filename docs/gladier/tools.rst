.. _tools:

Tools
=====

.. note::

   For the Python package containing pre-built and re-usable tools, see :ref:`gladier_tools_package`

As noted in A simple Gladier application, a Gladier application defines a set of tools that are
to be executed by the associated flow.

Gladier Tools are the glue that holds together Globus Flows and Compute Functions. A tool bundles
everything that a Compute Function needs to run, so that the Gladier Client can register the function,
check its requirements, and run it inside the Globus Flow.

The following code implements a simple tool, MakeDirs, that runs a single Compute Function, makedirs.



.. literalinclude:: example_tool.py
   :language: python

In the same module, this can be added to a client by simply adding the ``MakeDirs``
class to ``gladier_tools``:


.. code-block::

   # from gladier import GladierBaseClient
   @generate_flow_definition
   class ExampleClient(GladierBaseClient):
      gladier_tools = [MakeDirs]

A tool is composed of zero or more compute_functions and a flow_definition. A flow can be specified
explicitly, or if it involves just a single Compute Function, can be generated automatically by
using the @generate_flow_definition decorator. When applied to tools, this decorator will create
a simple one-state flow for the function to run.

The main attributes of a Gladier Tool are here:

* `compute_functions` (list of callables) – A list of functions this tool uses.
* `flow_input` (dict): Default input that should be used in the flow. This is automatically overridden if the user supplies flow input to the Gladier Client
* `required` (list of strings): A list of critical flow_input keys that must be present for the function to be run. Gladier will raise an exception if these are not present when the user attempts to run the flow.
* `flow_definition` (dict): (Optional) A complete Globus Flow for running this tool. Provides a built-in flow new users can use to instantly run your tool.

The :ref:`gladier_tools_package` package provides a set of predefined, generally useful tools for common tasks.
