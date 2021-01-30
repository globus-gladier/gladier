from gladier.defaults import GladierDefaults
from .funcx_functions import hello_world


class HelloWorld(GladierDefaults):

    flow_definition = {
        'Comment': 'Hello Gladier Automate Flow',
        'StartAt': 'HelloFuncX',
        'States': {
            'HelloFuncX': {
                'Comment': 'Say hello to the world!',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_id',
                        'func.$': '$.input.hello_world_funcx_id',
                        'payload': {
                            'data': {
                                'message.$': '$.input.message',
                            }
                        }
                    }]
                },
                'ResultPath': '$.HelloFuncXResult',
                'WaitTime': 300,
                'End': True,
            },
        }
    }

    flow_input = {
        'message': 'hello world',
    }

    funcx_funcions = [
        hello_world,
    ]
