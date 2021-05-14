from gladier import GladierBaseTool, GladierBaseClient

# Roughly simulates the look of a Globus Automate flow scope
mock_automate_flow_scope = ('https://auth.globus.org/scopes/mock_tool_flow_scope/'
                            'flow_mock_tool_flow_scope_user')


def mock_func(data):
    """Test mock function"""
    pass


class MockTool(GladierBaseTool):

    flow_definition = {
        'Comment': 'Say hello, maybe to a librarian.',
        'StartAt': 'MockFunc',
        'States': {
            'MockFunc': {
                'Comment': 'This func says the thing!',
                'Type': 'Action',
                'ActionUrl': 'https://api.funcx.org/automate',
                'ActionScope': 'https://auth.globus.org/scopes/'
                               'facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
                'ExceptionOnActionFailure': False,
                'Parameters': {
                    'tasks': [
                        {
                            'endpoint.$': '$.input.funcx_endpoint_non_compute',
                            'func.$': '$.input.hello_world_funcx_id',
                            'payload.$': '$.input'
                        }
                    ]
                },
                'ResultPath': '$.HelloWorld',
                'WaitTime': 300,
                'End': True
            },
        }
    }

    required_input = [
        'funcx_endpoint_non_compute'
    ]

    flow_input = {
        'funcx_endpoint_non_compute': 'my_non_compute_endpoint_uuid'
    }

    funcx_functions = [
        mock_func,
    ]


class MockGladierClient(GladierBaseClient):
    secret_config_filename = 'gladier-secrets.cfg'
    config_filename = 'gladier.cfg'

    gladier_tools = [
        'gladier.tests.test_data.gladier_mocks.MockTool'
    ]
    flow_definition = 'gladier.tests.test_data.gladier_mocks.MockTool'
