from gladier.client import GladierBaseClient
from pprint import pprint


class HelloGladier(GladierBaseClient):
    gladier_tools = [
        'gladier.tools.hello_world.HelloConversation',
    ]
    flow_definition = 'gladier.tools.hello_world.HelloConversation'


# Run the flow
hello_cli = HelloGladier()
flow_input = {
    'input': {
        'funcx_endpoint_non_compute': 'your_funcx_endpoint'
    }
}
flow = hello_cli.run_flow(flow_input=flow_input)

# Watch the progress, get the result.
hello_cli.progress(flow['action_id'])
pprint(hello_cli.get_status(flow['action_id']))
