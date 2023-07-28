from __future__ import annotations

from gladier import (
    StateWithNextOrEnd,
    StateWithParametersOrInputPath,
    StateWithResultPath,
    JSONObject,
)


class PassState(
    StateWithParametersOrInputPath,
    StateWithNextOrEnd,
    StateWithResultPath,
):
    state_type: str = "Pass"

    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()
