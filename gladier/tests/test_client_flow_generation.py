from gladier import GladierBaseClient, GladierBaseTool, generate_flow_definition
from globus_automate_client.flows_client import validate_flow_definition


def test_client_flow_generation_simple(logged_in):

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """Example Docs"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockTool'
        ]

    mc = MyClient()
    flow_def = mc.flow_definition
    assert isinstance(flow_def, dict)
    assert len(flow_def['States']) == 1
    assert flow_def['Comment'] == 'Example Docs'


def test_client_combine_gen_and_non_gen_flows(logged_in):

    def gen_tool_func():
        pass

    @generate_flow_definition
    class GeneratedTool(GladierBaseTool):
        """Mock Tool"""
        funcx_functions = [gen_tool_func]

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockTool',
            GeneratedTool,
        ]

    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 2
