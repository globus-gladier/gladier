import typing as t
import pytest
from gladier.tools.builtins import WaitState
from dataclasses import dataclass
from pydantic import ValidationError


@dataclass
class WaitStateTestCase:
    wait_props: t.Dict[str, t.Any]
    expected_state_props: t.Dict[str, t.Any]
    expected_exception: t.Optional[t.Type] = None


wait_test_cases = [
    WaitStateTestCase(wait_props={"seconds": 10}, expected_state_props={"Seconds": 10}),
    WaitStateTestCase(
        wait_props={"timestamp": "2001-01-01"},
        expected_state_props={},
        expected_exception=ValidationError,
    ),
    WaitStateTestCase(
        wait_props={"timestamp": "2001-01-01T00:10:28+00:00"},
        expected_state_props={"Timestamp": "2001-01-01T00:10:28+00:00"},
    ),
    WaitStateTestCase(
        wait_props={"timestamp_path": "foo"},
        expected_state_props={},
        expected_exception=ValidationError
    ),
    # TODO: A lot more cases
]


@pytest.mark.parametrize("test_case", wait_test_cases)
def test_wait_state(test_case: WaitStateTestCase):
    had_exception = False
    try:
        ws = WaitState(**test_case.wait_props)

        flow_def = ws.get_flow_definition()
        state_def = ws.get_flow_state_dict()
        found_expected = {k: state_def.get(k) for k in test_case.expected_state_props}
    except Exception as e:
        had_exception = True
        if test_case.expected_exception is None or not isinstance(
            e, test_case.expected_exception
        ):
            raise e
    if not had_exception:
        assert found_expected == test_case.expected_state_props
