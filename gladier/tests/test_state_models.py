from __future__ import annotations

import pytest

from gladier import GladierFlow, GladierStateWithNextOrEnd


class TestNextState(GladierStateWithNextOrEnd):
    state_type: str = "DummyTestState"


def test_next_chaining():
    state1 = TestNextState(state_name="state1")
    state1.next(TestNextState(state_name="state2")).next(
        TestNextState(state_name="state3")
    )
    flow = GladierFlow(start_at=state1)
    flow_def = flow.get_flow_definition()
    assert flow_def["StartAt"] == "state1"
    assert "States" in flow_def
    for expected_state in {"state1", "state2", "state3"}:
        assert expected_state in flow_def["States"], flow_def["States"].keys()


@pytest.mark.skip(reason="Flow generation for flows with loops is currently broken")
def test_looped_flow():
    state1 = TestNextState(state_name="state1")
    state2 = TestNextState(state_name="state2")
    state1.next(state2)
    state2.next(state1)

    flow = GladierFlow(start_at=state1)
    flow_def = flow.get_flow_definition()
    assert flow_def["StartAt"] == "state1"
    assert "States" in flow_def
    for expected_state in {"state1", "state2"}:
        assert expected_state in flow_def["States"], flow_def["States"].keys()
