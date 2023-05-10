from __future__ import annotations

from gladier import (
    GladierStateWithNextOrEnd,
    GladierStateWithParametersOrInputPath,
    GladierStateWithResultPath,
    JSONObject,
)


class PassState(
    GladierStateWithNextOrEnd,
    GladierStateWithParametersOrInputPath,
    GladierStateWithResultPath,
):
    state_type: str = "Pass"

    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()
