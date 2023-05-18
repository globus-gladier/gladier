from __future__ import annotations

import typing as t

from gladier import GladierBaseState, JSONObject


# TODO: add support here
class ChoiceState(GladierBaseState):
    state_type = "Choice"
    default: t.Optional[t.Union[str, GladierBaseState]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._choices = []

    def add_choice(
        self,
    ) -> GladierBaseState:
        # TODO Implement this by adding to self._choices
        return self

    def get_flow_definition(self) -> JSONObject:
        flow_def = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        # TODO: Add choices and default values to state_def
        return flow_def
