from __future__ import annotations

import typing as t

from pydantic import BaseModel

from gladier import GladierBaseState, JSONObject


class ChoiceOption(BaseModel):
    next: GladierBaseState


# TODO: add support here
class ChoiceState(GladierBaseState):
    state_type = "Choice"
    default: t.Optional[t.Union[str, GladierBaseState]] = None

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
        # TODO: Add choices and default values to state_def
        return flow_def

    def get_child_states(self) -> t.List[GladierBaseState]:
        return [self.default] + []
