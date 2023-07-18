from gladier import GladierBaseState, JSONObject


class SucceedState(GladierBaseState):
    state_type = "Succeed"

    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()
