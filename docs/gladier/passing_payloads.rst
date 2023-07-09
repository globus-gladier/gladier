Passing Payloads
================

This section shows how to pass outputs of one Compute Function to another using Globus Flows.


Simple Payloads
---------------

Sometimes you may need a state that depends on the output from another state. This can either be to
split up complex functions, or make Globus Compute Parallelize payloads into multiple simultanious tasks.

By default, all Gladier Tools take input from the main input source, defined as ``$.input``. However,
by using modifiers (see more in :ref:`flow_generation`), this default can be changed to use the
output of another compute function.

.. code-block:: python

    @generate_flow_definition(modifiers={
      my_second_function: {'payload': '$.MyFirstFunction.details.result[0]'},
    })
    class MyTool(GladierBaseTool):
        compute_functions = [
            my_first_function,
            my_second_function,
        ]

In the example above, the first function is given the full input to work with on ``$.input``. The output
of ``my_first_function`` will be produced with the name ``MyFirstFunction.details.result`` as a list of
Globus Compute task results. By default, only one Globus Compute task is run per-function, so typically this will be a list
with only one entry. The path ``$.MyFirstFunction.details.result[0]`` references the exact output returned
by a single invocation of ``my_first_function``.

.. note::

    Gladier Automatically creates flow state names by translating them from snake case to upper camel case.
    For example, ``my_first_function`` results in the state name ``MyFirstFunction``
 
When ``my_first_function`` finishes and ``my_second_function`` begins, it will be given the input stored in
``$.MyFirstFunction.details.result[0]``. This value **MUST** be a dictionary containing expected parameters
in ``my_second_function``, otherwise a flow exception will be raised and the flow will be marked as a failure.

.. warning::

    When using function outputs as payloads with ``ExceptionOnActionFailure: false``, this can result in cascading
    failures where the stringified exception results are used as input to the next function.
    It's recommended you either set ``ExceptionOnActionFailure: true`` or pass payloads as ``$.MyFirstFunction.details``.


Multiple Globus Compute Tasks
-----------------------------

Globus Compute is built to run many tasks in parallel. You can instruct Gladier to pass multiple task payloads with the ``tasks`` modifier.
However, at this level Globus Compute also needs an expcilit Compute endpoint and Function ID for each task it will process. It's common to
use one Compute function to build the list of payloads to be run in parallel. 

.. code-block:: python

    def parallel_workload_input_builder(compute_endpoint, parallel_workload_function_id, parallel_workloads, **data):
        return [{
            'endpoint': compute_endpoint,
            'function': parallel_workload_function_id,
            'payload': payload,
        } for payload in parallel_workloads]


    def parallel_workload(name, **data):
        import time
        return f'{name} finished at {time.time()}!'


    @generate_flow_definition(modifiers={
        parallel_workload: {'tasks': '$.ParallelWorkloadInputBuilder.details.result[0]'},
    })
    class ParallelWorkloadsTool(GladierBaseTool):
        comptue_functions = [
            parallel_workload_input_builder,
            parallel_workload,
        ]
        required_input = [
            'comptue_endpoint',
            'parallel_workloads',
            'parallel_workload_function_id'
        ]

Above, the ``parallel_workload_input_builder`` function is run first and generates the list of Globus Compute tasks. This can be an arbitrarily
long list determined at runtime. Each task in the list must contain three elements: ``endpoint``, ``function`` and ``payload``.

``endpoint`` above is typically specified by the user at input time, and is by default ``compute_endpoint``. But the Compute function
is updated by Gladier every change, and the name is determined automatically. By default, Gladier appends ``_function_id`` to the end of each
of the ``comptue_function`` definitions and automaticaly adds them to ``$.input``. ``parallel_workload_function_id`` can be determined above using
this method, or one can verify via the flow output.

``payload`` must be a dictonary containing keyword parameters for the function which match the function signature. This is similar to all other
Compute functions used in Gladier, which are called with all input data specified on ``$.input``.

When ``parallel_workload`` runs, it will execute all tasks in parallel, or by any rules defined by your particular compute endpoint. Each of the
outputs will be listed in ``$.ParallelWorkload.details.result`` once all tasks finish. If any task fails, a stack trace will be returned as a
string. If all tasks fail, the flow will be marked as "FAILED".

A full example of the Flow Definition as JSON output is below: 

.. code-block:: JSON

    {
    "Comment": "Flow with states: ParallelWorkloadInputBuilder, ParallelWorkload",
    "StartAt": "ParallelWorkloadInputBuilder",
    "States": {
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


Parallel Processing Example
---------------------------

Below is a full runnable example, using the Compute tutorial endpoint.

.. literalinclude:: passing_payloads.py
   :language: python