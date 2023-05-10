from __future__ import annotations

import typing as t

from gladier import GladierActionState, JSONObject
from gladier.managers import ComputeManager


class GlobusComputeStep(GladierActionState):
    endpoint_id: str = "$.input.globus_compute_endpoint"
    function_to_call: t.Union[t.Callable[[t.Any], t.Any], str]
    function_parameters: t.Union[t.Dict[str, t.Any], str]
    action_url = "https://compute.actions.globus.org/fxap"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.compute_manager = ComputeManager()

    def get_flow_definition(self) -> JSONObject:
        if not isinstance(self.function_to_call, str):
            function_id = self.compute_manager.register_function(
                self, self.function_to_call
            )
        else:
            function_id = self.function_to_call
        self.parameters = {
            "endpoint": self.endpoint_id,
            "function": function_id,
            "kwargs": self.function_parameters,
        }
        flow_definition = super().get_flow_definition()

        return flow_definition

    def set_call_params_from_self_model(
        self,
        model_prop_names: t.Union[t.Container[str], t.Iterable[str]],
        omit_Nones=False,
    ) -> JSONObject:
        self.function_parameters = {
            k: v
            for k, v in self.dict().items()
            if (k in model_prop_names and (not omit_Nones or v is not None))
        }
        return self.function_parameters
