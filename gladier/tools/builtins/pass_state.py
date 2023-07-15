from __future__ import annotations

from gladier import (
    GladierStateWithNextOrEnd,
    GladierStateWithParametersOrInputPath,
    StateWithResultPath,
    JSONObject,
)


class PassState(
    GladierStateWithNextOrEnd,
    GladierStateWithParametersOrInputPath,
    StateWithResultPath,
):
    state_type: str = "Pass"

    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()
