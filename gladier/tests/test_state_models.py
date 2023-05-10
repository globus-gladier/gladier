from __future__ import annotations

import typing as t

import pytest
from gladier import (
    GladierBaseClient,
    GladierBaseState,
    GladierBaseTool,
    GladierStateWithNextOrEnd,
    generate_flow_definition,
)


def mock_func(data):
    """Test mock function"""
    pass


class TestNextState(GladierStateWithNextOrEnd):
    state_type: str = "DummyTestState"


def _three_step_flow() -> GladierBaseState:
    state1 = TestNextState(state_name="state1")
    state1.next(TestNextState(state_name="state2")).next(
        TestNextState(state_name="state3")
    )
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
    state1 = TestNextState(state_name="state1")
    state2 = TestNextState(state_name="state2")
    state1.next(state2)
    state2.next(state1)

    flow = GladierBaseClient(start_at=state1)
    flow_def = flow.get_flow_definition()
    assert flow_def["StartAt"] == "state1"
    assert "States" in flow_def
    for expected_state in {"state1", "state2"}:
        assert expected_state in flow_def["States"], flow_def["States"].keys()
