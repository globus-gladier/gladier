from gladier.client import GladierClient
from pprint import pprint


class HelloGladier(GladierClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier.tools.hello_world.HelloWorld',
    ]
    flow_definition = 'gladier.tools.hello_world.HelloWorld'


hello_cli = HelloGladier()
flow = hello_cli.start_flow()
hello_cli.progress(flow['action_id'])
details = hello_cli.get_details(flow['action_id'], 'HelloFuncXResult')
pprint(details)