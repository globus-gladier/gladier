from gladier import GladierBaseClient, GladierBaseTool, generate_flow_definition
from pprint import pprint


def parallel_workload_input_builder(funcx_endpoint_compute, parallel_workload_funcx_id, parallel_workloads, **data):
    return [{
        'endpoint': funcx_endpoint_compute,
        'function': parallel_workload_funcx_id,
        'payload': payload,
    } for payload in parallel_workloads]


def parallel_workload(name, **data):
    import time
    return f'{name} finished at {time.time()}!'


@generate_flow_definition(modifiers={
    parallel_workload: {'tasks': '$.ParallelWorkloadInputBuilder.details.result[0]'},
})
class ParallelWorkloadsTool(GladierBaseTool):
    funcx_functions = [
        parallel_workload_input_builder,
        parallel_workload,
    ]
    required_input = [
        'funcx_endpoint_compute',
        'parallel_workloads',
        'parallel_workload_funcx_id'
    ]


@generate_flow_definition
class ParallelWorkloadsClient(GladierBaseClient):
    gladier_tools = [
        ParallelWorkloadsTool,
    ]


if __name__ == '__main__':
    flow_input = {
        'input': {
            'parallel_workloads': [
                {'name': 'foo'},
                {'name': 'bar'},
                {'name': 'baz'},
            ],
            'funcx_endpoint_compute': '553e7b64-0480-473c-beef-be762ba979a9',
        }
    }
    work_flow = ParallelWorkloadsClient()
    pprint(work_flow.flow_definition)

    flow = work_flow.run_flow(flow_input=flow_input)
    run_id = flow['run_id']
    work_flow.progress(run_id)
    pprint(work_flow.get_status(run_id))

