from __future__ import annotations

import typing as t


def exclusive_validator_generator(
    exclusive_property_names: t.List[str], require_one_set=True
):
    def exclusive_generator(cls, v, values: t.Dict[str, t.Any], field, **kwargs):
        found: t.List[str] = []
        if v is not None:
            found.append(field.name)
        for exclusive_prop in exclusive_property_names:
            model_val = values.get(exclusive_prop)
            if model_val is not None:
                found.append(model_val)
        if len(found) == 1 or len(found) == 0 and not require_one_set:
            return v

        if require_one_set:
            error_prefix = "Exactly"
        else:
            error_prefix = "At most"
        raise ValueError(
            f"{error_prefix} one of {exclusive_property_names} may be set for "
            f"model class {cls.__name__}, found values for properties "
            f"{found}"
        )

    return exclusive_generator


def validate_path_property(cls, v, values: t.Dict[str, t.Any], field: t.Any, **kwargs):
    if field.name.lower().endswith("path") and not str(v).startswith("$."):
        raise ValueError(
            f"Field named {field.name} must have a JSONPath value, got {v}"
        )
    return v
