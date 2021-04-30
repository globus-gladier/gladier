from gladier import GladierBaseTool


def hello_world(message):
    return message


class HelloWorld(GladierBaseTool):

    flow_definition = {
        'Comment': 'Hello Gladier Automate Flow',
        'StartAt': 'HelloFuncX',
        'States': {
            'HelloFuncX': {
                'Comment': 'Say hello to the world!',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'ExceptionOnActionFailure': False,
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.hello_world_funcx_id',
                        'payload.$': '$.input.message'
                    }]
                },
                'ResultPath': '$.HelloFuncXResult',
                'WaitTime': 300,
                'End': True,
            },
        }
    }

    required_input = [
        'message',
        'funcx_endpoint_non_compute'
    ]

    flow_input = {
        'message': 'hello world',
    }

    funcx_functions = [
        hello_world,
    ]
