from __future__ import annotations

import datetime
import typing as t

from pydantic import validator
from pydantic.fields import ModelField

from gladier import GladierStateWithNextOrEnd, JSONObject

_wait_state_exclusives_list = ["seconds", "timestamp", "seconds_path", "timestamp_path"]


class WaitState(GladierStateWithNextOrEnd):
    state_type: str = "Wait"
    seconds: t.Optional[int] = None
    timestamp: t.Optional[datetime.datetime] = None
    seconds_path: t.Optional[str] = None
    timestamp_path: t.Optional[str] = None

    @validator(*_wait_state_exclusives_list)
    def validate_exclusive_properties(
        cls, v, values: t.Dict[str, t.Any], field: ModelField, **kwargs
    ):
        found: t.List[str] = []
        if v is not None:
            found.append(field.name)
        for exclusive_prop in _wait_state_exclusives_list:
            model_val = values.get(exclusive_prop)
            if model_val is not None:
                found.append(model_val)
        if len(found) != 1:
            raise ValueError(
                f"Exactly one of {_wait_state_exclusives_list} may be set for "
                f"model class {cls.__name__}, found values for properties "
                f"{found}"
            )
        return v

    @validator("timestamp_path", "seconds_path")
    def validate_json_path(cls, v, field: ModelField):
        if v is not None and not v.startswith("$."):
            raise ValueError(
                f"Field {field.name} must be in JSONPath format "
                "(starting with the prefix $.)"
            )
        return v

    def get_flow_definition(self) -> JSONObject:
        flow_def = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        if self.seconds is not None:
            state_def["Seconds"] = self.seconds
        elif self.timestamp is not None:
            state_def["Timestamp"] = self.timestamp.isoformat()
        elif self.seconds_path is not None:
            state_def["SecondsPath"] = self.seconds_path
        elif self.timestamp_path is not None:
            state_def["TimestampPath"] = self.timestamp_path

        return flow_def
