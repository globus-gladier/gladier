import typing as t

from gladier import ActionState, JSONObject
from pydantic import BaseModel


class GlobusTransferItem(BaseModel):
    source_path: str
    destination_path: str
    recursive: t.Optional[t.Union[bool, str]] = None


class GlobusTransfer(ActionState):
    action_url = "https://actions.globus.org/transfer/transfer"
    source_endpoint_id: str  # Could/should add validation for a UUID
    destination_endpoint_id: str
    transfer_items: t.Union[t.List[GlobusTransferItem], str]
    notify_on_succeeded: t.Optional[t.Union[bool, str]] = None
    notify_on_failed: t.Optional[t.Union[bool, str]] = None
    notify_on_inactive: t.Optional[t.Union[bool, str]] = None
