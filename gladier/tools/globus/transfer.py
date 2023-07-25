import typing as t

from gladier import JSONObject
from gladier.tools.builtins import ActionState
from pydantic import BaseModel


class GlobusTransferItem(BaseModel):
    source_path: str = "$.input.source_transfer_path"
    destination_path: str = "$.input.destination_transfer_path"
    recursive: t.Optional[t.Union[bool, str]] = None


class GlobusTransfer(ActionState):
    action_url = "https://actions.globus.org/transfer/transfer"
    source_endpoint_id: str = "$.input.transfer_source_endpoint_id"
    destination_endpoint_id: str = "$.input.transfer_destination_endpoint_id"
    transfer_items: t.Union[t.List[GlobusTransferItem], str] = [GlobusTransferItem()]
    notify_on_succeeded: t.Optional[t.Union[bool, str]] = None
    notify_on_failed: t.Optional[t.Union[bool, str]] = None
    notify_on_inactive: t.Optional[t.Union[bool, str]] = None


class GlobusTransferDelete(ActionState):
    action_url = "https://actions.globus.org/transfer/delete"
    endpoint_id: str = "$.input.transfer_delete_endpoint_id"
    ignore_missing: t.Optional[t.Union[bool, str]] = None
    interpret_globs: t.Optional[t.Union[bool, str]] = None
    items: t.Union[t.List[str], str] = "$.input.transfer_delete_items"
    label: t.Optional[str] = None
    notify_on_succeeded: t.Optional[t.Union[bool, str]] = None
    notify_on_failed: t.Optional[t.Union[bool, str]] = None
    notify_on_inactive: t.Optional[t.Union[bool, str]] = None
    recursive: t.Optional[bool] = None
