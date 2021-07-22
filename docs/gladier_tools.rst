
Gladier Tools
-------------

Gladier Tools are the glue that holds together Globus Flows and FuncX functions.
Tools bundle everything the FuncX function needs to run, so the Glaider Client
can register the function, check the requirements, and run it inside the Globus Flow.

Additionally, Gladier Tools can come with their own built-in ``flow_definition`` for
running the tool standalone without other tools. This is handy if the tool is complex,
and users would benefit from tinkering with it directly before installing it into a
larger Globus Flow.

The main attributes of a Gladier Tool are here:

* funcx_functions (list of callables) -- A list of functions this tool uses.
* flow_input (dict) -- Default input that should be used in the flow. This is automatically
  overrided if the user supplies flow input to the Gladier Client
* required_input (list of strings) -- A list of critical Funcx flow_input keys that **must**
  be present for the function to be run. Gladier will raise an exception if these are
  not present when the user attempts to run the flow.
* flow_definition (dict) -- (Optional) A complete Globus Flow for running this tool. Provides
  a built-in flow new users can use to instantly run your tool.


A full "Hello World" Tool definition looks like this:

.. literalinclude:: tools/hello_world_tool.py
   :language: python
   :pyobject: HelloWorld
