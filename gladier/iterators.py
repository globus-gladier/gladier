from __future__ import annotations

import copy
import typing as t
from glob import glob

from globus_automate_client import get_authorizer_for_scope
from globus_sdk.services.transfer import TransferClient
from globus_sdk.services.transfer.client import TransferFilterDict, UUIDLike

from .helpers import JSONObject, JSONValue, deep_update_dict, insert_json_path

_TRANSFER_ALL_SCOPE = "urn:globus:auth:scope:transfer.api.globus.org:all"


def templated_flow_input_generator(
    values: t.Iterable[JSONValue], input_template: JSONObject, value_json_path: str
) -> t.Iterator[JSONObject]:
    for value in values:
        flow_input = copy.deepcopy(input_template)
        insert_json_path(flow_input, value_json_path, value)
        yield flow_input


def nested_flow_input_generator(
    input_generators: t.List[t.Iterable[JSONObject]],
) -> t.Iterator[JSONObject]:
    for input_val in input_generators[0]:
        print(f"read value: {input_val}")
        if len(input_generators) > 1:
            for nested_input_val in nested_flow_input_generator(input_generators[1:]):
                yield_val = copy.deepcopy(input_val)
                print(f"nested val: {nested_input_val}")
                deep_update_dict(yield_val, nested_input_val)
                print(f"nested yield: {yield_val}")
                yield yield_val
        else:
            print(f"Simple yield: {input_val}")
            yield input_val


def glob_iterator(
    pathname: str, input_template: JSONObject, value_json_path: str, recursive=False
) -> t.Iterator[JSONObject]:
    return templated_flow_input_generator(
        glob(pathname, recursive=recursive), input_template, value_json_path
    )


def globus_collection_iterator(
    endpoint_id: UUIDLike,
    path: str,
    input_template: JSONObject,
    value_json_path: str,
    transfer_client: TransferClient | None = None,
    filt: str | t.List[str] | TransferFilterDict | None = None,
) -> t.Iterator[JSONObject]:
    if transfer_client is None:
        authorizer = get_authorizer_for_scope(_TRANSFER_ALL_SCOPE)
        transfer_client = TransferClient(authorizer=authorizer)
    return templated_flow_input_generator(
        transfer_client.operation_ls(endpoint_id, path, filter=filt),
        input_template,
        value_json_path,
    )
