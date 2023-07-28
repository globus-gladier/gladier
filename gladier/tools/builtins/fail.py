import typing as t
from gladier import GladierBaseState, JSONObject


class FailState(GladierBaseState):
    state_type = "Fail"
    cause: t.Optional[str] = None
    error: t.Optional[str] = None

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        if self.cause is not None:
            flow_state["Cause"] = self.cause
        if self.error is not None:
            flow_state["Error"] = self.error
        return flow_definition
