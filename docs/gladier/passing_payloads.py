from gladier import GladierBaseClient, GladierBaseTool, generate_flow_definition
from pprint import pprint


def parallel_workload_input_builder(
    compute_endpoint, parallel_workload_function_id, parallel_workloads, **data
):
    return [
        {
            "endpoint": compute_endpoint,
            "function": parallel_workload_function_id,
            "payload": payload,
        }
        for payload in parallel_workloads
    ]


def parallel_workload(name, **data):
    import time

    return f"{name} finished at {time.time()}!"


@generate_flow_definition(
    modifiers={
        parallel_workload: {
            "tasks": "$.ParallelWorkloadInputBuilder.details.results[0].output"
        },
    }
)
class ParallelWorkloadsTool(GladierBaseTool):
    compute_functions = [
        parallel_workload_input_builder,
        parallel_workload,
    ]
    required_input = [
        "compute_endpoint",
        "parallel_workloads",
        "parallel_workload_function_id",
    ]


@generate_flow_definition
class ParallelWorkloadsClient(GladierBaseClient):
    gladier_tools = [
        ParallelWorkloadsTool,
    ]


if __name__ == "__main__":
    flow_input = {
        "input": {
            "parallel_workloads": [
                {"name": "foo"},
                {"name": "bar"},
                {"name": "baz"},
            ],
            "compute_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
        }
    }
    work_flow = ParallelWorkloadsClient()
    # Optionally shohw details of the flow input and definition
    print("Using Input:")
    pprint(work_flow.get_input())
    print("\n\nFlow Definition: ")
    pprint(work_flow.flow_definition)

    flow = work_flow.run_flow(flow_input=flow_input)
    run_id = flow["run_id"]
    work_flow.progress(run_id)
    pprint(work_flow.get_status(run_id))
