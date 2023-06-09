from __future__ import annotations

import typing as t

from pydantic import BaseModel

from gladier import GladierBaseState, JSONObject


class ChoiceRule(BaseModel):
    def flow_dict(self) -> JSONObject:
        return self.dict(exclude_none=True, exclude_unset=True)


_Comparison_rule_operators = [
    "BooleanEquals",
    "BooleanEqualsPath",
    "IsBoolean",
    "IsNull",
    "IsNumeric",
    "IsPresent",
    "IsString",
    "IsTimestamp",
    "NumericEquals",
    "NumericEqualsPath",
    "NumericGreaterThan",
    "NumericGreaterThanPath",
    "NumericGreaterThanEquals",
    "NumericGreaterThanEqualsPath",
    "NumericLessThan",
    "NumericLessThanPath",
    "NumericLessThanEquals",
    "NumericLessThanEqualsPath",
    "StringEquals",
    "StringEqualsPath",
    "StringGreaterThan",
    "StringGreaterThanPath",
    "StringGreaterThanEquals",
    "StringGreaterThanEqualsPath",
    "StringLessThan",
    "StringLessThanPath",
    "StringLessThanEquals",
    "StringLessThanEqualsPath",
    "StringMatches",
    "TimestampEquals",
    "TimestampEqualsPath",
    "TimestampGreaterThan",
    "TimestampGreaterThanPath",
    "TimestampGreaterThanEquals",
    "TimestampGreaterThanEqualsPath",
    "TimestampLessThan",
    "TimestampLessThanPath",
    "TimestampLessThanEquals",
    "TimestampLessThanEqualsPath",
]


class ComparisonRule(ChoiceRule):
    Variable: str

    BooleanEquals: t.Optional[str] = None
    BooleanEqualsPath: t.Optional[str] = None
    IsBoolean: t.Optional[str] = None
    IsNull: t.Optional[str] = None
    IsNumeric: t.Optional[str] = None
    IsPresent: t.Optional[str] = None
    IsString: t.Optional[str] = None
    IsTimestamp: t.Optional[str] = None
    NumericEquals: t.Optional[str] = None
    NumericEqualsPath: t.Optional[str] = None
    NumericGreaterThan: t.Optional[str] = None
    NumericGreaterThanPath: t.Optional[str] = None
    NumericGreaterThanEquals: t.Optional[str] = None
    NumericGreaterThanEqualsPath: t.Optional[str] = None
    NumericLessThan: t.Optional[str] = None
    NumericLessThanPath: t.Optional[str] = None
    NumericLessThanEquals: t.Optional[str] = None
    NumericLessThanEqualsPath: t.Optional[str] = None
    StringEquals: t.Optional[str] = None
    StringEqualsPath: t.Optional[str] = None
    StringGreaterThan: t.Optional[str] = None
    StringGreaterThanPath: t.Optional[str] = None
    StringGreaterThanEquals: t.Optional[str] = None
    StringGreaterThanEqualsPath: t.Optional[str] = None
    StringLessThan: t.Optional[str] = None
    StringLessThanPath: t.Optional[str] = None
    StringLessThanEquals: t.Optional[str] = None
    StringLessThanEqualsPath: t.Optional[str] = None
    StringMatches: t.Optional[str] = None
    TimestampEquals: t.Optional[str] = None
    TimestampEqualsPath: t.Optional[str] = None
    TimestampGreaterThan: t.Optional[str] = None
    TimestampGreaterThanPath: t.Optional[str] = None
    TimestampGreaterThanEquals: t.Optional[str] = None
    TimestampGreaterThanEqualsPath: t.Optional[str] = None
    TimestampLessThan: t.Optional[str] = None
    TimestampLessThanPath: t.Optional[str] = None
    TimestampLessThanEquals: t.Optional[str] = None
    TimestampLessThanEqualsPath: t.Optional[str] = None


class AndRule(ChoiceRule):
    __root__: t.List[ChoiceRule]

    def __init__(self, rules: t.List[ChoiceRule], *args, **kwargs):
        super().__init__(__root__=rules, *args, **kwargs)

    def flow_dict(self) -> JSONObject:
        fd: JSONObject = {"And": [cr.flow_dict() for cr in self.__root__]}
        return fd


class OrRule(ChoiceRule):
    __root__: t.List[ChoiceRule]

    def __init__(self, rules: t.List[ChoiceRule], *args, **kwargs):
        super().__init__(__root__=rules, *args, **kwargs)


class NotRule(ChoiceRule):
    __root__: ChoiceRule

    def __init__(self, rule: ChoiceRule, *args, **kwargs):
        super().__init__(__root__=rule, *args, **kwargs)


class ChoiceOption(BaseModel):
    rule: ChoiceRule
    next: GladierBaseState

    def flow_dict(self) -> JSONObject:
        fd = self.rule.flow_dict()
        fd["Next"] = self.next.valid_state_name
        return fd


# TODO: add support here
class ChoiceState(GladierBaseState):
    state_type = "Choice"
    rules: t.List[ChoiceRule] = []
    default: t.Optional[GladierBaseState] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._choices: t.List[ChoiceOption] = []

    def choice(self, choice_option: ChoiceOption) -> GladierBaseState:
        self._choices.append(choice_option)
        return self

    def set_default(self, default_choice: GladierBaseState) -> GladierBaseState:
        self.default = default_choice
        return self.default

    def get_flow_definition(self) -> JSONObject:
        flow_def = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        if isinstance(self.default, GladierBaseState):
            state_def["Default"] = self.default.valid_state_name
        state_def["Choices"] = [cr.flow_dict() for cr in self._choices]
        return flow_def

    def get_child_states(self) -> t.List[GladierBaseState]:
        return (
            [choice.next for choice in self._choices] + [self.default]
            if self.default is not None
            else []
        )
