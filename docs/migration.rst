Upgrade Migrations
==================


Migrating to v0.9.0
-------------------

Funcx was removed in favor of the new Globus Compute SDK, requiring changes in Gladier Tools.
The main changes are demonstrated on the tool below:

.. code-block:: python

   @generate_flow_definition(modifiers={
      # The path of outputs has changed in Globus Compute from the following:
      # MyTask.details.result[0] --> MyTask.details.results[0].output
      # WARNING: Gladier tools with modifiers MUST change funcx_functions to compute_functions
      parallel_workload: {'tasks': '$.ParallelWorkloadInputBuilder.details.results[0].output'},
   })
   class ParallelWorkloadsTool(GladierBaseTool):

      # Previously named "funcx_functions". This will continue to work for most tools UNLESS the tool
      # defines modifiers above, which will raise an exception. All tools should migrate to "compute_functions"
      compute_functions = [
         parallel_workload_input_builder,
         parallel_workload,
      ]

      required_input = [
         # The convention for endpoint names have changed. Previous names were: funcx_endpoint_compute and funcx_endpoint_non_compute
         # New names only include "compute_endpoint"
         'compute_endpoint',
         'parallel_workloads',
         # function names have changed from myfunc_funcx_id --> myfunc_function_id. These are generated automatically, and should not
         # affect most usage.
         'parallel_workload_function_id'
      ]


The full list of required changes are below:

* Gladier Base Tool "funcx_functions" changed to "compute_functions"
    * Old tools will still be backwards compatible, but will use newer function names instead
    * Tools should be migrated to use compute_functions instead of funcx_functions
    * Using modifiers with old tools will raise an exception in v0.9.0
* Input Functions named previously "{name}_funcx_id" are now "{name}_function_id"
* Default "funcx_endpoint_compute" name changed to "compute_endpoint"
    * Naming convention "funcx_endpoint_non_compute" and "funcx_endpoint_compute" have been dropped and are no longer used,
      however users are still free to name custom endpoints using modifiers to any chosen value.
* Default action URL is now ``https://compute.actions.globus.org``
* Task output format changed, previously ``$.MyTask.details.result[0]`` is now ``$.MyTask.details.results[0].output``
    * Both styles are currently outputted for backwards compatibility. All tooling should switch to the newer style.

For any tool developers using full flow definitions, the following example shows usage for the newest values and convestions:

.. code-block:: JSON

   {
      "States": {
         "Comment": "Flow with states: ParallelWorkloadInputBuilder, ParallelWorkload",
         "StartAt": "ParallelWorkloadInputBuilder",
         "ParallelWorkloadInputBuilder": {
            "Comment": null,
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org",
            "ExceptionOnActionFailure": false,
            "Parameters": {
            "tasks": [
               {
                  "endpoint.$": "$.input.compute_endpoint",
                  "function.$": "$.input.parallel_workload_input_builder_function_id",
                  "payload.$": "$.input"
               }
            ]
            },
            "ResultPath": "$.ParallelWorkloadInputBuilder",
            "WaitTime": 300,
            "Next": "ParallelWorkload"
         },
         "ParallelWorkload": {
            "Comment": null,
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org",
            "ExceptionOnActionFailure": false,
            "Parameters": {
            "tasks.$": "$.ParallelWorkloadInputBuilder.details.results[0].output"
            },
            "ResultPath": "$.ParallelWorkload",
            "WaitTime": 300,
            "End": true
         }
      }
   }

Migrating to v0.6.0 -- v0.8.0
-----------------------------

No features added in these releases require changes


Migrating to v0.5.0
-------------------

The only major change in v0.5.0 was the removal of the HelloWorld Tools from the
main Gladier package. The following are no longer present:

* ``gladier.tools.hello_world.HelloWorld``
* ``gladier.tools.manifest.ManifestTransfer``
* ``gladier.tools.manifest.ManifestToFuncXTasks``

There currently aren't plans to rewrite them in the Gladier Tools package, but
open an issue if you would like us to consider changing that!

Migrating to v0.4.0
-------------------

Gladier v0.3.x depended on FuncX v0.0.5 and FuncX Endpoint v0.0.3. Gladier v0.4.x
now uses Funcx v0.2.3-v0.3.0+ (funcx-endpoint v0.2.3-v0.3.0+). There are a number
of breaking changes between these two versions of FuncX, including funcx endpoints,
flow definitions, and backend services.

FuncX Endpoints
^^^^^^^^^^^^^^^

All FuncX endpoints will need to be recreated with the never version of FuncX.
Gladier typically names these endpoints as the following:

* ``funcx_endpoint_non_compute``
* ``funcx_endpoint_compute``

Since these use different backend services, using endpoints that don't match the
FuncX version will result in errors. Using 0.0.3 endponits on 0.2.3+ will result
in permission denied, using 0.2.3+ on 0.0.3 will result in Server 500s.

Argument Passing and Function Definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Previously, all arguments in a Flow were passed to FuncX functions as a dict. It
looked like the following:

.. code-block::

  'Parameters': {'tasks': [{'endpoint.$': '$.input.funcx_endpoint_non_compute',
                            'function': '8227609b-4869-4c6f-9a1b-87dc49fcc687',
                            'payload.$': '$.input'}]},

  def my_function(data):
      ...


In the above, ``data`` would get the entire dict from $.input, which was typically
whatever input was passed to start the flow. In the new version of FuncX, this has
changed. All arguments are either positional or keyword arguments and should be named.
This is difficult in automate, since naming arguments requires specifying them
explicitly in the flow definition. An easy migration path is the following:

.. code-block::

  'Parameters': {'tasks': [{'endpoint.$': '$.input.funcx_endpoint_non_compute',
                            'function': '8227609b-4869-4c6f-9a1b-87dc49fcc687',
                            'payload.$': '$.input'}]},

  def my_function(**data):
      ...

Changing data to a keyword argument will allow re-creating the same behavior as
before.


FuncX Functions
^^^^^^^^^^^^^^^

Like FuncX Endpoints, FuncX Functions also need to be changed between versions.
This is an automatic process in most cases if you are running the latest version
of Gladier and saw a big giant warning when upgrading. Gladier will automatically
delete funcx functions that don't match the newly supported version of FuncX
Gladier uses.

However, it's necessary to do a manual upgrade to remove these functions in some
cases. To upgrade manually, edit the file ``~/.gladier-secrets.cfg``, and remove
all config items that end in ``funcx_id`` and ``funcx_id_checksum``:


.. code-block::

   hello_world_funcx_id = 3bccfcdb-bc0e-4549-9297-8e08c6f50bd5
   hello_world_funcx_id_checksum = c590423de52051e7b7bb044dc173673d2c9ad965f7f71bee665494815b3a2046


Flow Definitions
^^^^^^^^^^^^^^^^

Some items in Automate flow definitions also changed. See below for a list of
the attributes.

FuncX Version 0.0.5 flow definitions:

* ``ActionUrl`` -- 'https://api.funcx.org/automate'
* ``ActionScope`` -- 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2'


FuncX Version 0.2.3+ flow definitions:


* ``ActionUrl`` -- 'https://automate.funcx.org'
* ``ActionScope`` -- 'https://auth.globus.org/scopes/b3db7e59-a6f1-4947-95c2-59d6b7a70f8c/action_all'


Additionally for FuncX Payloads, Function UUIDs are passed with a different name.


'func.$': '$.input.'

Needs to be changed to:

'function.$': '$.input.'

FuncX Flow Result Format
^^^^^^^^^^^^^^^^^^^^^^^^

The format of the return value from FuncX functions has changed format. This only
affects Flow states that depend on the output of a FuncX function/flow state.

Previous flow states were not returned in a list, and were referenced with the following:


.. code-block::

   'InputPath': '$.MyFuncXFunctionOutput.details.result',

FuncX now returns these in a list, and they need to be index. The above needs to be changed
to the following:

.. code-block::

   'InputPath': '$.MyFuncXFunctionOutput.details.result[0]',
