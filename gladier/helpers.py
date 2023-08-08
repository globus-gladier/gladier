import typing as t

from typing_extensions import TypeAlias

JSONObject: TypeAlias = t.Dict[str, "JSONValue"]
JSONList: TypeAlias = t.Iterable["JSONValue"]
JSONValue: TypeAlias = t.Union[JSONObject, JSONList, str, int, float, bool, None]


def deep_update_dict(
    dest_dict: t.Dict[str, t.Any], from_dict: t.Dict[str, t.Any]
) -> t.Dict[str, t.Any]:
    """Update all sub-dicts for a given dict."""
    for k, v in from_dict.items():
        if isinstance(dest_dict.get(k), dict) and isinstance(v, dict):
            deep_update_dict(dest_dict[k], v)
        else:
            dest_dict[k] = v
    return dest_dict


def ensure_json_path(path: t.Optional[str]) -> t.Optional[str]:
    """Ensure the given parameter ``path`` is prefixed with "$.". Does nothing
    if the given path already starts with "$.", and so is safe to call multiple times."""
    if path is not None and not path.startswith("$."):
        path = "$." + path
    return path


def eliminate_none_values(d: t.Dict[t.Any, t.Any], deep=False) -> None:
    """Remove all items from a dictionary where the values are None."""
    keys_to_pop = []
    for k, v in d.items():
        if v is None:
            keys_to_pop.append(k)
        if deep and isinstance(v, dict):
            eliminate_none_values(v, deep)
        elif deep and isinstance(v, list):
            for list_val in v:
                if isinstance(list_val, dict):
                    eliminate_none_values(list_val, deep)

    for k in keys_to_pop:
        d.pop(k)


def ensure_parameter_values(
    params: JSONObject, deep=True, eliminate_none_values=False
) -> JSONObject:
    """
    For a given flow definition snippet, iterate through all of the objects within and ensure
    that JSON path prefixes have been set correctly on the keys and values. For example,
    {"foo": "$.bar"} will be fixed to show {"foo.$": "$.bar"}.
    """
    ret_obj: JSONObject = {}
    for k, v in params.items():
        # If the value is a pydantic model (or anything else supporting a dict() method)
        # unmarshall it into a dict to be used in the parameters
        if v is not None:
            try:
                v = v.dict()
            except AttributeError:
                pass

        if isinstance(v, str):
            if k.endswith(".$") and not v.startswith("$."):
                v = "$." + v
            elif v.startswith("$.") and not k.endswith(".$"):
                k = k + ".$"
            elif v.startswith("=") and not k.endswith(".="):
                k = k + ".="
                v = v[1:]
        elif deep and isinstance(v, dict):
            v = ensure_parameter_values(
                v, deep=deep, eliminate_none_values=eliminate_none_values
            )
        elif deep and isinstance(v, list):
            new_v = []
            for list_val in v:
                if isinstance(list_val, dict):
                    list_val = ensure_parameter_values(
                        list_val, deep=deep, eliminate_none_values=eliminate_none_values
                    )
                new_v.append(list_val)
            v = new_v
        ret_obj[k] = v
    return ret_obj
