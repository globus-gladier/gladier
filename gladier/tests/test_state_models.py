from __future__ import annotations

import typing as t

import pytest
from gladier import (
    GladierBaseClient,
    GladierBaseState,
    GladierBaseTool,
    GladierClient,
    StateWithNextOrEnd,
    generate_flow_definition,
)
from gladier.tools.builtins import ActionExceptionName, ActionState


def mock_func(data):
    """Test mock function"""
    pass


class SimpleTestState(ActionState):
    action_url = "https://fake_state.com/ap"


_default_test_states = ("state1", "state2", "state3")


def _create_test_flow_sequence(test_states=_default_test_states) -> GladierBaseState:
    start_at: t.Optional[SimpleTestState] = None
    for state_name in test_states:
        test_state = SimpleTestState(state_name=state_name)
        if start_at is None:
            start_at = test_state
        else:
            # By re-assigning start_at to the return from next, we emulate the behavior
            # of chained calls to next()
            start_at = start_at.next(test_state)
    return start_at


def _test_flow_definition_sequence(
    flow_def: t.Dict[str, t.Any], test_expected_state_sequence=_default_test_states
):
    assert flow_def["StartAt"] == test_expected_state_sequence[0]
    assert "States" in flow_def
    prev_state_name: t.Optional[str] = None
    for expected_state in test_expected_state_sequence:
        assert expected_state in flow_def["States"], flow_def["States"].keys()
        if prev_state_name is not None:
            assert flow_def["States"][prev_state_name]["Next"] == expected_state
        prev_state_name = expected_state


def test_base_client_startat():
    client = GladierClient(
        flow_definition=_create_test_flow_sequence().get_flow_definition()
    )
    flow_def = client.get_flow_definition()
    _test_flow_definition_sequence(flow_def)


def test_base_client_subclass():
    @generate_flow_definition
    class TestClient(GladierBaseClient):
        gladier_tools = [_create_test_flow_sequence()]

    test_client = TestClient()
    flow_def = test_client.get_flow_definition()
    _test_flow_definition_sequence(flow_def)


def test_action_with_exception_handler():
    parent_action = SimpleTestState(state_name="ParentState")
    parent_action.set_exception_handler(
        ActionExceptionName.States_All, SimpleTestState(state_name="AllHandler")
    )
    parent_action.set_exception_handler(
        ActionExceptionName.ActionUnableToRun, SimpleTestState(state_name="AllHandler")
    )

    flow_def = parent_action.get_flow_definition()
    # This tests that both the parent and the handler state are in the generated flow,
    # and also that they both have their End state set to True as they should since
    # neither has a next() call made on it
    for state_name in {"ParentState", "AllHandler"}:
        assert flow_def["States"][state_name]["End"] is True
    catches = flow_def["States"]["ParentState"]["Catch"]
    assert len(catches) == 1, catches
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
        gladier_tools = [_create_test_flow_sequence(), MockTool]

    test_client = TestClient()
    flow_def = test_client.get_flow_definition()

    _test_flow_definition_sequence(flow_def)
    assert "MockFunc" in flow_def["States"]
    assert flow_def["States"]["state3"]["Next"] == "MockFunc"


def test_insert_next():
    start_at = _create_test_flow_sequence()
    start_at.next(SimpleTestState(state_name="Inserted"), insert_next=True)
    flow_def = start_at.get_flow_definition()
    _test_flow_definition_sequence(
        flow_def, (_default_test_states[0], "Inserted") + _default_test_states[1:]
    )


def test_replace_next():
    start_at = _create_test_flow_sequence()
    start_at.next(SimpleTestState(state_name="Replaced"), replace_next=True)
    flow_def = start_at.get_flow_definition()
    _test_flow_definition_sequence(flow_def, (_default_test_states[0], "Replaced"))


@pytest.mark.skip(reason="Flow generation for flows with loops is currently broken")
def test_looped_flow():
    state1 = SimpleTestState(state_name="state1")
    state2 = SimpleTestState(state_name="state2")
    state1.next(state2)
    state2.next(state1)

    flow = GladierBaseClient(start_at=state1)
    flow_def = flow.get_flow_definition()
    assert flow_def["StartAt"] == "state1"
    assert "States" in flow_def
    for expected_state in {"state1", "state2"}:
        assert expected_state in flow_def["States"], flow_def["States"].keys()
