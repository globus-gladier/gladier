from __future__ import annotations

import datetime
import typing as t

from pydantic import validator
from pydantic.fields import ModelField

from gladier import GladierStateWithNextOrEnd, JSONObject
from gladier.tools import exclusive_validator_generator

_wait_state_exclusives_list = ["seconds", "timestamp", "seconds_path", "timestamp_path"]


class WaitState(GladierStateWithNextOrEnd):
    state_type: str = "Wait"
    seconds: t.Optional[int] = None
    timestamp: t.Optional[datetime.datetime] = None
    seconds_path: t.Optional[str] = None
    timestamp_path: t.Optional[str] = None

    exclusive_validator = exclusive_validator_generator(
        _wait_state_exclusives_list, require_one_set=True
    )

    @validator(*_wait_state_exclusives_list)
    def validate_exclusive_properties(
        cls, v, values: t.Dict[str, t.Any], field: ModelField, **kwargs
    ):
        return cls.exclusive_validator(cls, v, values, field, **kwargs)

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
