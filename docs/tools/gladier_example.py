from gladier import GladierBaseClient
from pprint import pprint


class HelloGladier(GladierBaseClient):
    gladier_tools = [
        'gladier.tools.hello_world.HelloWorld',
    ]
    flow_definition = 'gladier.tools.hello_world.HelloWorld'


hello_cli = HelloGladier()
flow_input = {
    'input': {
        'funcx_endpoint_non_compute': '<your_funcx_endpoint>',
    }
}
flow = hello_cli.run_flow(flow_input=flow_input)
hello_cli.progress(flow['action_id'])
details = hello_cli.get_details(flow['action_id'], 'HelloFuncXResult')
pprint(details)
