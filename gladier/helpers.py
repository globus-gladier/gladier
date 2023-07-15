import typing as t

from jsonpath_ng import parse as parse_jsonpath
from jsonpath_ng.exceptions import JsonPathParserError
from typing_extensions import TypeAlias

JSONObject: TypeAlias = t.Dict[str, "JSONValue"]
JSONList: TypeAlias = t.Iterable["JSONValue"]
JSONValue: TypeAlias = t.Union[JSONObject, JSONList, str, int, float, bool, None]


def deep_update_dict(
    dest_dict: t.Dict[str, t.Any], from_dict: t.Dict[str, t.Any]
) -> t.Dict[str, t.Any]:
    for k, v in from_dict.items():
        if isinstance(dest_dict.get(k), dict) and isinstance(v, dict):
            deep_update_dict(dest_dict[k], v)
        else:
            dest_dict[k] = v
    return dest_dict


def ensure_json_path(path: t.Optional[str]) -> t.Optional[str]:
    if path is not None and not path.startswith("$."):
        path = "$." + path
    return path


def eliminate_none_values(d: t.Dict[t.Any, t.Any], deep=False) -> None:
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


def insure_parameter_values(
    params: JSONObject, deep=True, eliminate_none_values=False
) -> JSONObject:
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
            v = insure_parameter_values(
                v, deep=deep, eliminate_none_values=eliminate_none_values
            )
        elif deep and isinstance(v, list):
            new_v = []
            for list_val in v:
                if isinstance(list_val, dict):
                    list_val = insure_parameter_values(
                        list_val, deep=deep, eliminate_none_values=eliminate_none_values
                    )
                new_v.append(list_val)
            v = new_v
        ret_obj[k] = v
    return ret_obj


def eval_jsonpath_for_input(json_path: str, flow_input: JSONObject) -> t.Any:
    try:
        expression = parse_jsonpath(json_path)
    except JsonPathParserError:
        return json_path
    result = expression.find(flow_input)
    return result[0].value


def insert_json_path(
    json_obj: JSONObject, json_path: str, value: JSONValue
) -> JSONObject:
    path_elements = json_path.split(".")
    store_to_dict = json_obj
    if path_elements[0] != "$":
        raise ValueError(f"JSONPath string must start with '$.', got {json_path}")
    for path_element in path_elements[1:-1]:
        path_val = store_to_dict.get(path_element)
        if not isinstance(path_val, dict):
            store_to_dict[path_element] = dict()
        store_to_dict = store_to_dict[path_element]
    store_to_dict[path_elements[-1]] = value
    return json_obj
