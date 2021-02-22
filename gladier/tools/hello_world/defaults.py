from gladier.defaults import GladierDefaults
from .funcx_functions import hello_world, hello_pause, hello_exception


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
        # Shamelessly reuse the FuncX Tutorial Endpoint if it doesn't exist
        'funcx_endpoint_non_compute': '4b116d3c-1703-4f8f-9f6f-39921e5864df'
    }

    funcx_functions = [
        hello_world,
    ]


class HelloConversation(GladierDefaults):

    flow_definition = {
        'Comment': 'Hello Gladier Automate Flow',
        'StartAt': 'Greeting',
        'States': {
            'Greeting': {
                'Comment': 'Say something to start the conversation',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.hello_pause_funcx_id',
                        'payload': {
                            'message.$': '$.input.greeting',
                            'delay.$': '$.input.delay',
                        }
                    }]
                },
                'ResultPath': '$.GreetingResult',
                'WaitTime': 300,
                'Next': 'Conversation',
            },
            'Conversation': {
                'Comment': 'Say something interesting',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.hello_pause_funcx_id',
                        'payload': {
                            'message.$': '$.input.conversation',
                            'delay.$': '$.input.delay',
                        }
                    }]
                },
                'ResultPath': '$.ConversationResult',
                'WaitTime': 300,
                'Next': 'Goodbye',
            },
            'Goodbye': {
                'Comment': 'Find a way to gracefully eject yourself from this encounter.',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': '$.input.hello_pause_funcx_id',
                        'payload': {
                            'message.$': '$.input.goodbye',
                            'delay.$': '$.input.delay',
                        }
                    }]
                },
                'ResultPath': '$.GoodbyeResult',
                'WaitTime': 300,
                'End': True,
            },
        }
    }

    required_input = [
        'greeting',
        'conversation',
        'goodbye',
        'funcx_endpoint_non_compute'
    ]

    flow_input = {
        'greeting': 'How are you today?',
        'conversation': 'The weather sure is nice today',
        'goodbye': 'Talk to you later!',
        # Shamelessly reuse the FuncX Tutorial Endpoint if it doesn't exist
        'funcx_endpoint_non_compute': '4b116d3c-1703-4f8f-9f6f-39921e5864df'
    }

    funcx_functions = [
        hello_pause,
    ]


class HelloException(GladierDefaults):

    flow_definition = {
        'Comment': "Hello Gladier Automate Flow Exception. This flow isn't much for conversation",
        'StartAt': 'HelloException',
        'States': {
            'HelloException': {
                'Comment': 'Say hello... maybe.',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'Parameters': {
                    'tasks': [{
                        'endpoint.$': '$.input.funcx_endpoint_non_compute',
                        'func.$': f'$.input.hello_exception_funcx_id',
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
        # Shamelessly reuse the FuncX Tutorial Endpoint if it doesn't exist
        'funcx_endpoint_non_compute': '4b116d3c-1703-4f8f-9f6f-39921e5864df'
    }

    funcx_functions = [
        hello_exception,
    ]
