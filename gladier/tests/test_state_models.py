from __future__ import annotations

import typing as t

import pytest
from gladier import (
    ActionState,
    ActionExceptionName,
    GladierBaseClient,
    GladierBaseState,
    GladierBaseTool,
    StateWithNextOrEnd,
    generate_flow_definition,
)


def mock_func(data):
    """Test mock function"""
    pass


class TestState(ActionState):
    action_url = "https://fake_state.com/ap"


def _three_step_flow() -> GladierBaseState:
    state1 = TestState(state_name="state1")
    state1.next(TestState(state_name="state2")).next(TestState(state_name="state3"))
    return state1


def _test_three_step_flow_definition(flow_def: t.Dict[str, t.Any]):
    assert flow_def["StartAt"] == "state1"
    assert "States" in flow_def
    for expected_state in {"state1", "state2", "state3"}:
        assert expected_state in flow_def["States"], flow_def["States"].keys()


def test_base_client_startat():
    client = GladierBaseClient(start_at=_three_step_flow())
    flow_def = client.get_flow_definition()
    _test_three_step_flow_definition(flow_def)


def test_base_client_subclass():
    @generate_flow_definition
    class TestClient(GladierBaseClient):
        gladier_tools = [_three_step_flow()]

    test_client = TestClient()
    flow_def = test_client.get_flow_definition()
    _test_three_step_flow_definition(flow_def)


def test_action_with_exception_handler():
    parent_action = TestState(state_name="ParentState")
    parent_action.set_exception_handler(
        ActionExceptionName.States_All, TestState(state_name="AllHandler")
    )
    parent_action.set_exception_handler(
        ActionExceptionName.ActionUnableToRun, TestState(state_name="AllHandler")
    )

    flow_def = parent_action.get_flow_definition()
    # This tests that both the parent and the handler state are in the generated flow,
    # and also that they both have their End state set to True as they should since
    # neither has a next() call made on it
    for state_name in {"ParentState", "AllHandler"}:
        assert flow_def["States"][state_name]["End"] is True
    catches = flow_def["States"]["ParentState"]["Catch"]
    assert len(catches) ==  1, catches
    assert (
        ActionExceptionName.States_All.value in catches[0]["ErrorEquals"]
        and ActionExceptionName.ActionUnableToRun.value in catches[0]["ErrorEquals"]
    )



def test_mixed_state_model_and_tool():
    @generate_flow_definition
    class MockTool(GladierBaseTool):
        """Mock Tool"""

        compute_functions = [mock_func]

    @generate_flow_definition
    class TestClient(GladierBaseClient):
        gladier_tools = [_three_step_flow(), MockTool]

    test_client = TestClient()
    flow_def = test_client.get_flow_definition()

    _test_three_step_flow_definition(flow_def)
    assert "MockFunc" in flow_def["States"]
    assert flow_def["States"]["state3"]["Next"] == "MockFunc"


@pytest.mark.skip(reason="Flow generation for flows with loops is currently broken")
def test_looped_flow():
    state1 = TestState(state_name="state1")
    state2 = TestState(state_name="state2")
    state1.next(state2)
    state2.next(state1)

    flow = GladierBaseClient(start_at=state1)
    flow_def = flow.get_flow_definition()
    assert flow_def["StartAt"] == "state1"
    assert "States" in flow_def
    for expected_state in {"state1", "state2"}:
        assert expected_state in flow_def["States"], flow_def["States"].keys()
