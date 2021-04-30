from gladier import GladierBaseTool


def hello_exception(message):
    raise Exception(message)


class HelloException(GladierBaseTool):

    flow_definition = {
        'Comment': "Hello Gladier Automate Flow Exception. This flow isn't much for conversation",
        'StartAt': 'HelloException',
        'States': {
            'HelloException': {
                'Comment': 'Say hello... maybe.',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'ExceptionOnActionFailure': False,
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.hello_exception_funcx_id',
                        'payload.$': '$.input.exception_message'
                    }]
                },
                'ResultPath': '$.HelloExceptionResult',
                'WaitTime': 300,
                'End': True,
            },
        }
    }

    required_input = [
        'exception_message',
        'funcx_endpoint_non_compute'
    ]

    flow_input = {
        'exception_message': 'Hello Exception!',
    }

    funcx_functions = [
        hello_exception,
    ]
