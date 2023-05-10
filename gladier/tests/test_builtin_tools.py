from __future__ import annotations

import typing as t
from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from gladier.tools.builtins import (
    AndRule,
    ChoiceOption,
    ChoiceState,
    ComparisonRule,
    PassState,
    WaitState,
)


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
        expected_exception=ValidationError,
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


def test_choice_state():
    cr1 = ComparisonRule(Variable="$.foo", StringLessThan="zzz")
    cr2 = ComparisonRule(Variable="$.bar", TimestampEquals="111")
    and_rule = AndRule([cr1, cr2])
    co = ChoiceOption(rule=and_rule, next=PassState(state_name="ChoiceTarget"))
    default_target = PassState(state_name="DefaultTarget")
    choice_state = ChoiceState(state_name="ChoiceState", default=default_target)
    choice_state.choice(co)
    flow_def = choice_state.get_flow_definition()

    assert flow_def["StartAt"] == choice_state.valid_state_name
    for state_name in {
        choice_state.valid_state_name,
        default_target.valid_state_name,
        "ChoiceTarget",
    }:
        assert state_name in flow_def["States"]


def test_choice_rule_bad_jsonpath():
    with pytest.raises(ValidationError):
        cr1 = ComparisonRule(Variable="$.foo", StringLessThanPath="zzz")


def test_choice_rule_good_jsonpath():
    cr1 = ComparisonRule(Variable="$.foo", StringLessThanPath="$.zzz")


def test_choice_rule_multiple_tests():
    with pytest.raises(ValidationError):
        cr1 = ComparisonRule(
            Variable="$.foo", StringLessThan="zzz", BooleanEquals="False"
        )
