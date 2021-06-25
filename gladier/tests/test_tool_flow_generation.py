import pytest
from gladier.base import GladierBaseTool
from gladier.decorators import generate_flow_definition
from gladier.exc import FlowGenException
from globus_automate_client.flows_client import validate_flow_definition


def mock_func(data):
    """Test mock function"""
    pass


def mock_func2(data):
    pass


def test_tool_generate_basic_flow_no_mods():

    @generate_flow_definition
    class MockTool(GladierBaseTool):
        """Mock Tool"""
        funcx_functions = [mock_func]

    tool = MockTool()
    fd = tool.flow_definition
    validate_flow_definition(fd)
    assert isinstance(fd, dict)
    assert fd['Comment'] == 'Mock Tool'
    assert fd['StartAt'] == 'MockFunc'
    assert set(fd['States']) == {'MockFunc'}
    assert fd['States']['MockFunc']['Comment'] == 'Test mock function'


def test_tool_generate_multiple_states():

    @generate_flow_definition
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    validate_flow_definition(fd)
    assert isinstance(fd, dict)
    assert fd['Comment'] == 'Flow with states: MockFunc, MockFunc2'
    assert fd['StartAt'] == 'MockFunc'
    assert len(fd['States']) == 2
    assert set(fd['States']) == {'MockFunc', 'MockFunc2'}


def test_tool_generate_no_states():

    @generate_flow_definition
    class MockTool(GladierBaseTool):
        pass

    with pytest.raises(FlowGenException):
        MockTool()


def test_tool_endpoint_mods():
    @generate_flow_definition(modifiers={
        mock_func: {'endpoint': 'my_weirdly_named_funcx_endpoint'}
    })
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func]

    tool = MockTool()
    fd = tool.flow_definition
    fx_ep = fd['States']['MockFunc']['Parameters']['tasks'][0]['endpoint.$']
    assert fx_ep == '$.input.my_weirdly_named_funcx_endpoint'


def test_tool_custom_payload():
    @generate_flow_definition(modifiers={
        mock_func: {
            'payload': '$.MyCustomInput.details.result',
            'endpoint': '$.HiddenEndpoints.foo'
        }
    })
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd['States']['MockFunc']['Parameters']['tasks'][0]
    assert fx_task['endpoint.$'] == '$.HiddenEndpoints.foo'
    assert fx_task['payload.$'] == '$.MyCustomInput.details.result'


def test_tool_modifier_dependent_payloads():
    @generate_flow_definition(modifiers={
        mock_func2: {
            'payload': mock_func,
        }
    })
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd['States']['MockFunc2']['Parameters']['tasks'][0]
    assert fx_task['payload.$'] == '$.MockFunc.details.results'


def test_tool_modifier_by_func_name_payloads():
    @generate_flow_definition(modifiers={
        'mock_func2': {
            'payload': 'mock_func',
        }
    })
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd['States']['MockFunc2']['Parameters']['tasks'][0]
    assert fx_task['payload.$'] == '$.MockFunc.details.results'


def test_tool_modifier_by_state_name_payloads():
    @generate_flow_definition(modifiers={
        'mock_func2': {
            'payload': 'MockFunc',
        }
    })
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd['States']['MockFunc2']['Parameters']['tasks'][0]
    assert fx_task['payload.$'] == '$.MockFunc.details.results'


def test_tool_modifier_custom_name_payloads():
    @generate_flow_definition(modifiers={
        'mock_func2': {
            'payload': '$.MyStuff.details.results',
        }
    })
    class MockTool(GladierBaseTool):
        funcx_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd['States']['MockFunc2']['Parameters']['tasks'][0]
    assert fx_task['payload.$'] == '$.MyStuff.details.results'
