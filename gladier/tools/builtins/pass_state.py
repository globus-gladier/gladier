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
    """Pass states contain no operations and are typically used to signify different
    transitional states between operational logic in a flow. For instance, if there was
    optional logic that the user may want to skip as part of a flow, a pass state could
    define the location where the optional logic ends and flow execution should pick back
    up (Likely chosen by a Choice state)"""

    state_type: str = "Pass"

    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()
