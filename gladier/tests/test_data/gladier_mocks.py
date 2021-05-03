from gladier import GladierBaseTool, GladierBaseClient

# Roughly simulates the look of a Globus Automate flow scope
mock_automate_flow_scope = ('https://auth.globus.org/scopes/mock_tool_flow_scope/'
                            'flow_mock_tool_flow_scope_user')


def mock_func(data):
    pass


class MockTool(GladierBaseTool):

    flow_definition = {'Mock': 'Globus Flow'}

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
