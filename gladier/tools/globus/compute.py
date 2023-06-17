from __future__ import annotations

import hashlib
import json
import typing as t
from pathlib import Path

from gladier import GladierActionState, JSONObject
from globus_compute_sdk import Client as ComputeClient
from globus_compute_sdk.serialize import ComputeSerializer

_cache_file = Path.home() / ".gladier_function_id_cache.json"


def hash_for_callable(cllable: t.Callable[[t.Any], t.Any]) -> str:
    serializer = ComputeSerializer()
    serial = serializer.serialize(cllable)
    sha256 = hashlib.sha256()
    sha256.update(bytes(serial, "utf-8"))
    return sha256.hexdigest()


def get_globus_compute_function_cache() -> t.Dict[str, t.Tuple[str, str]]:
    try:
        with open(_cache_file, "r") as f:
            cache = json.load(f)
            return cache
    except FileNotFoundError:
        return {}


def save_globus_compute_function_cache(cache: t.Dict[str, t.Tuple[str, str]]) -> None:
    with open(_cache_file, "w") as f:
        json.dump(cache, f, indent=2)


def register_function_with_compute(cllable: t.Callable[[t.Any], t.Any]) -> str:
    compute_client = ComputeClient()
    cllable_id = compute_client.register_function(cllable)
    return cllable_id


def globus_compute_id_for_callable(cllable: t.Callable[[t.Any], t.Any]) -> str:
    cllable_hash = hash_for_callable(cllable)
    cache = get_globus_compute_function_cache()
    try:
        return cache[cllable_hash][0]
    except KeyError:
        cllable_id = register_function_with_compute(cllable)
        cache[cllable_hash] = (cllable_id, cllable.__name__)
        save_globus_compute_function_cache(cache)

    return cllable_id


class GlobusComputeStep(GladierActionState):
    endpoint_id: str = "$.input.globus_compute_endpoint"
    function_to_call: t.Union[t.Callable[[t.Any], t.Any], str]
    function_parameters: t.Union[t.Dict[str, t.Any], str]
    action_url = "https://compute.actions.globus.org/fxap"

    def get_flow_definition(self) -> JSONObject:
        if not isinstance(self.function_to_call, str):
            function_id = globus_compute_id_for_callable(self.function_to_call)
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
