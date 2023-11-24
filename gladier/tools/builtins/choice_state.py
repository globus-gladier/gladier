from __future__ import annotations

import typing as t

from pydantic import BaseModel, validator
from pydantic.fields import ModelField

from gladier import BaseCompositeState, BaseState, JSONObject, StateWithNextOrEnd
from gladier.tools.helpers import exclusive_validator_generator, validate_path_property


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

    BooleanEquals: t.Optional[bool] = None
    BooleanEqualsPath: t.Optional[str] = None
    IsBoolean: t.Optional[bool] = None
    IsNull: t.Optional[bool] = None
    IsNumeric: t.Optional[bool] = None
    IsPresent: t.Optional[bool] = None
    IsString: t.Optional[bool] = None
    IsTimestamp: t.Optional[bool] = None
    NumericEquals: t.Optional[float] = None
    NumericEqualsPath: t.Optional[str] = None
    NumericGreaterThan: t.Optional[float] = None
    NumericGreaterThanPath: t.Optional[str] = None
    NumericGreaterThanEquals: t.Optional[float] = None
    NumericGreaterThanEqualsPath: t.Optional[str] = None
    NumericLessThan: t.Optional[float] = None
    NumericLessThanPath: t.Optional[str] = None
    NumericLessThanEquals: t.Optional[float] = None
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

    exclusive_validator = exclusive_validator_generator(
        _Comparison_rule_operators, require_one_set=True
    )

    @validator(*_Comparison_rule_operators)
    def validate_exclusive_properties(
        cls, v, values: t.Dict[str, t.Any], field: ModelField, **kwargs
    ):
        return cls.exclusive_validator(cls, v, values, field, **kwargs)

    @validator(*_Comparison_rule_operators)
    def validate_path_properties(
        cls, v, values: t.Dict[str, t.Any], field: ModelField, **kwargs
    ):
        return validate_path_property(cls, v, values, field, **kwargs)


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
    next: BaseState

    def flow_dict(self) -> JSONObject:
        fd = self.rule.flow_dict()
        fd["Next"] = self.next.valid_state_name
        return fd


# TODO: add support here
class ChoiceState(BaseState):
    """
    The Choice state allows for branching logic depending on a set of conditions.

    An example is below:

    .. code-block:: python

        from gladier.tools import ChoiceState, ChoiceOption, ComparisonRule, FailState, PassState
        from gladier import GladierClient


        choice_state = (
            ChoiceState()
            .choice(
                ChoiceOption(
                    rule=ComparisonRule(
                        Variable="$.input.myvar", NumericEquals=0.0
                    ),
                    next=FailState(
                        cause="Random value 0 selected",
                        error="Unluck 0 selected, simulated error",
                    ),
                )
            ))
        choice_state.set_default(PassState(state_name="SuccessfulCompletion"))

        gc = GladierClient(choice_state.get_flow_definition())
        gc.run_flow(flow_input={'input': {'myvar': 1}})

    See the full list of Comparison Rules above, and operations.

    """

    state_type = "Choice"
    rules: t.List[ChoiceRule] = []
    default: t.Optional[BaseState] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._choices: t.List[ChoiceOption] = []

    def choice(self, choice_option: ChoiceOption) -> BaseState:
        self._choices.append(choice_option)
        return self

    def set_default(self, default_choice: BaseState) -> BaseState:
        self.default = default_choice
        return self.default

    def get_flow_definition(self) -> JSONObject:
        flow_def = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        if isinstance(self.default, BaseState):
            state_def["Default"] = self.default.valid_state_name
        state_def["Choices"] = [cr.flow_dict() for cr in self._choices]
        return flow_def

    def get_child_states(self) -> t.List[BaseState]:
        return (
            [choice.next for choice in self._choices] + [self.default]
            if self.default is not None
            else []
        )


class ChoiceSkipState(BaseCompositeState):
    rule: ChoiceRule
    state_for_rule: StateWithNextOrEnd

    def construct_flow(self) -> ChoiceState:
        if not hasattr(self, "_next_state"):
            raise ValueError(
                f"For state {self.state_name} next() must be set prior to "
                "generating the flow definition"
            )
        choice_state = ChoiceState(state_name=self.state_name, default=self._next_state)
        choice_state.choice(ChoiceOption(rule=self.rule, next=self.state_for_rule))
        self.state_for_rule.next(self._next_state, replace_next=True)
        return choice_state

    def next(
        self,
        next_state: BaseState,
        for_state: t.Optional[t.Union[str, BaseState]] = None,
    ) -> BaseState:
        self._next_state = next_state
        return self
