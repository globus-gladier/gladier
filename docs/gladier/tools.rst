
Tools
-----

.. literalinclude:: example_tool.py
   :language: python

Gladier Tools are the glue that holds together Globus Flows and FuncX functions.
Tools bundle everything the FuncX function needs to run, so the Glaider Client
can register the function, check the requirements, and run it inside the Globus Flow.

Each tool is composed of zero or more ``funcx_functions`` and a ``flow_definition``.
Flows can be specified explicitly, or if they are a single FuncX function they can
be generated automatically using the ``@generate_flow_definition`` decorator. When applied
to tools, ``@generate_flow_definition`` will create a simple one-state flow for the function
to run.

The main attributes of a Gladier Tool are here:

* funcx_functions (list of callables) -- A list of functions this tool uses.
* flow_input (dict) -- Default input that should be used in the flow. This is automatically
  overrided if the user supplies flow input to the Gladier Client
* required (list of strings) -- A list of critical Funcx flow_input keys that **must**
  be present for the function to be run. Gladier will raise an exception if these are
  not present when the user attempts to run the flow.
* flow_definition (dict) -- (Optional) A complete Globus Flow for running this tool. Provides
  a built-in flow new users can use to instantly run your tool.
