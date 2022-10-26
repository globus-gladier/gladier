import pytest
from gladier import GladierBaseClient, GladierBaseTool, generate_flow_definition, exc
from globus_automate_client.flows_client import validate_flow_definition
from gladier.utils.tool_alias import StateSuffixVariablePrefix


def gen_tool_func():
    pass


@generate_flow_definition
class GeneratedTool(GladierBaseTool):
    """Mock Tool"""
    funcx_functions = [gen_tool_func]


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


def test_client_flow_generation_two_tools_two_inst(logged_in):
    """Previously, this caused a KeyError due to overwriting a flow on a tool."""

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """Example Docs"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockTool',
            GeneratedTool,
        ]

    MyClient()
    mc = MyClient()
    flow_def = mc.flow_definition
    assert isinstance(flow_def, dict)
    assert len(flow_def['States']) == 2
    assert flow_def['Comment'] == 'Example Docs'


def test_client_combine_gen_and_non_gen_flows(logged_in):

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


def test_client_tool_with_three_steps(logged_in):

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockToolThreeStates',
        ]

    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 3


def test_client_tool_with_no_flow(logged_in):

    class MyTool(GladierBaseTool):
        flow_definition = None

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        gladier_tools = [
            MyTool,
        ]

    with pytest.raises(exc.FlowGenException):
        MyClient()


def test_client_tool_duplication(logged_in):
    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockTool',
            'gladier.tests.test_data.gladier_mocks.MockTool:MockTool2',
            'gladier.tests.test_data.gladier_mocks.MockTool:MockTool3',
        ]

    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 3
    assert set(flow_def['States']) == {'MockFunc', 'MockFuncMockTool2', 'MockFuncMockTool3'}


def test_client_tool_duplication_with_generated_defs(logged_in):

    @generate_flow_definition
    class Sorted(GladierBaseTool):
        funcx_functions = [sorted]

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            Sorted(alias='First', alias_class=StateSuffixVariablePrefix),
            Sorted(alias='Second', alias_class=StateSuffixVariablePrefix),
        ]
    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 2
    assert set(flow_def['States']) == {'SortedFirst', 'SortedSecond'}


def test_client_tool_duplication_with_generated_def_strs(logged_in):
    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.GeneratedTool:First',
            'gladier.tests.test_data.gladier_mocks.GeneratedTool:Second',
        ]
    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 2
    assert set(flow_def['States']) == {'MockFuncFirst', 'MockFuncSecond'}


def test_client_tool_complex_duplication(logged_in):
    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockToolThreeStates',
            'gladier.tests.test_data.gladier_mocks.MockToolThreeStates:DoItAgain',
            'gladier.tests.test_data.gladier_mocks.MockToolThreeStates:DoItRightThisTime',
        ]

    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 9
    assert set(flow_def['States']) == {
        'StateOne',
        'StateOneDoItAgain',
        'StateOneDoItRightThisTime',
        'StateTwo',
        'StateTwoDoItAgain',
        'StateTwoDoItRightThisTime',
        'StateThree',
        'StateThreeDoItAgain',
        'StateThreeDoItRightThisTime',
    }


def test_client_tool_conflicting_state_names(logged_in):
    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """My very cool Client"""
        gladier_tools = [
            'gladier.tests.test_data.gladier_mocks.MockTool',
            'gladier.tests.test_data.gladier_mocks.MockTool',
        ]
    with pytest.raises(exc.StateNameConflict):
        MyClient()


def test_choice_state_tool_chaining(logged_in):
    class MyTool(GladierBaseTool):
        flow_transition_states = ['1b']
        flow_definition = {
            'StartAt': '1a',
            'States': {
                '1a': {
                    'Type': 'Choice',
                    'Default': '2a',
                    'Choices': [{
                        'Next': '1b',
                        'Variable': '$.foo',
                        'IsPresent': True,
                    }]
                },
                '2a': {
                    'Type': 'Pass',
                    'End': True
                },
                '1b': {
                    'Type': 'Pass',
                    'End': True
                }
            }
        }

    @generate_flow_definition
    class MyClient(GladierBaseClient):
        """Example Docs"""
        gladier_tools = [
            MyTool,
            'gladier.tests.test_data.gladier_mocks.MockTool',
        ]

    mc = MyClient()
    flow_def = mc.flow_definition
    validate_flow_definition(flow_def)
    assert len(flow_def['States']) == 4
    assert flow_def['States']['MockFunc'].get('Next') is None
    # Chain should add 'next' in transition state 1b
    assert 'Next' in flow_def['States']['1b']
    assert flow_def['States']['1b']['Next'] == 'MockFunc'
