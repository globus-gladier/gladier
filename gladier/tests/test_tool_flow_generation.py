import pytest
from gladier.base import GladierBaseTool
from gladier.decorators import generate_flow_definition
from gladier.exc import FlowGenException, FlowModifierException
from gladier import GladierBaseClient


def mock_func(data):
    """Test mock function"""
    pass


def mock_func2(data):
    pass


def test_tool_generate_basic_flow_no_mods():
    @generate_flow_definition
    class MockTool(GladierBaseTool):
        """Mock Tool"""

        compute_functions = [mock_func]

    tool = MockTool()
    fd = tool.flow_definition
    assert isinstance(fd, dict)
    assert fd["Comment"] == "Flow with states: MockFunc"
    assert fd["StartAt"] == "MockFunc"
    assert set(fd["States"]) == {"MockFunc"}
    assert fd["States"]["MockFunc"]["Comment"] == "Test mock function"


def test_tool_generate_multiple_states():
    @generate_flow_definition
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    assert isinstance(fd, dict)
    assert fd["Comment"] == "Flow with states: MockFunc, MockFunc2"
    assert fd["StartAt"] == "MockFunc"
    assert len(fd["States"]) == 2
    assert set(fd["States"]) == {"MockFunc", "MockFunc2"}
    assert fd["States"]["MockFunc"]["Next"] == "MockFunc2"
    assert fd["States"]["MockFunc2"]["End"] is True


def test_tool_duplicate_compute_functions():
    @generate_flow_definition
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func, mock_func]

    with pytest.raises(FlowGenException):
        MockTool()


def test_tool_generate_no_states():
    @generate_flow_definition
    class MockTool(GladierBaseTool):
        pass

    with pytest.raises(FlowGenException):
        MockTool()


def test_tool_endpoint_mods():
    @generate_flow_definition(
        modifiers={mock_func: {"endpoint": "my_weirdly_named_compute_endpoint"}}
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func]

    tool = MockTool()
    fd = tool.flow_definition
    assert "MockFunc" in fd["States"]
    fx_ep = fd["States"]["MockFunc"]["Parameters"]["tasks"][0]["endpoint.$"]
    assert fx_ep == "$.input.my_weirdly_named_compute_endpoint"


def test_tool_custom_payload():
    @generate_flow_definition(
        modifiers={
            mock_func: {
                "payload": "$.MyCustomInput.details.result",
                "endpoint": "$.HiddenEndpoints.foo",
            }
        }
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd["States"]["MockFunc"]["Parameters"]["tasks"][0]
    assert fx_task["endpoint.$"] == "$.HiddenEndpoints.foo"
    assert fx_task["payload.$"] == "$.MyCustomInput.details.result"


def test_tool_modifier_dependent_payloads():
    @generate_flow_definition(
        modifiers={
            mock_func2: {
                "payload": mock_func,
            }
        }
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd["States"]["MockFunc2"]["Parameters"]["tasks"][0]
    assert fx_task["payload.$"] == "$.MockFunc.details.results"


def test_tool_modifier_by_func_name_payloads():
    @generate_flow_definition(
        modifiers={
            "mock_func2": {
                "payload": "mock_func",
            }
        }
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd["States"]["MockFunc2"]["Parameters"]["tasks"][0]
    assert fx_task["payload.$"] == "$.MockFunc.details.results"


def test_tool_modifier_by_state_name_payloads():
    @generate_flow_definition(
        modifiers={
            "mock_func2": {
                "payload": "MockFunc",
            }
        }
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd["States"]["MockFunc2"]["Parameters"]["tasks"][0]
    assert fx_task["payload.$"] == "$.MockFunc.details.results"


def test_tool_modifier_custom_name_payloads():
    @generate_flow_definition(
        modifiers={
            "mock_func2": {
                "payload": "$.MyStuff.details.results",
            }
        }
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func, mock_func2]

    tool = MockTool()
    fd = tool.flow_definition
    fx_task = fd["States"]["MockFunc2"]["Parameters"]["tasks"][0]
    assert fx_task["payload.$"] == "$.MyStuff.details.results"


def test_tool_custom_action_url():
    @generate_flow_definition(
        modifiers={
            "mock_func": {
                "ActionUrl": "https://myap.example.com",
            }
        }
    )
    class MockTool(GladierBaseTool):
        compute_functions = [mock_func]

    tool = MockTool()
    assert (
        tool.flow_definition["States"]["MockFunc"]["ActionUrl"]
        == "https://myap.example.com"
    )


def test_generated_flow_with_old_tool():
    @generate_flow_definition
    class MyLegacyTool(GladierBaseTool):
        required_input = [
            "funcx_endpoint_non_compute",
        ]

        funcx_functions = [
            mock_func,
        ]

    @generate_flow_definition(
        modifiers={
            "mock_func": {
                "payload": "$.Foo.details.result[0]",
                "WaitTime": 600,
            }
        }
    )
    class MyClient(GladierBaseClient):
        gladier_tools = [MyLegacyTool]

    with pytest.raises(FlowModifierException):
        MyClient()
