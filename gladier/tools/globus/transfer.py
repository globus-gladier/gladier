import typing as t

from gladier import JSONObject
from gladier.tools.builtins import ActionState
from pydantic import BaseModel


class TransferItem(BaseModel):
    source_path: str = "$.input.source_transfer_path"
    destination_path: str = "$.input.destination_transfer_path"
    recursive: t.Optional[t.Union[bool, str]] = None


class Transfer(ActionState):
    """
    Action Provider State for transferring files from one collection to another.

    Example:

    .. code-block:: python

        from gladier import GladierClient
        from gladier.tools import GlobusTransfer

        client = GladierClient(flow_definition=GlobusTransfer().get_flow_definition())
        flow_run = client.run_flow(
            {"input": {
                "transfer_source_endpoint_id": "ddb59aef-6d04-11e5-ba46-22000b92c6ec",
                "transfer_destination_endpoint_id": "ddb59aef-6d04-11e5-ba46-22000b92c6ec",
                "source_transfer_path": "/share/godata",
                "destination_transfer_path": "~/"
            }}
        )

    """

    action_url = "https://actions.globus.org/transfer/transfer"
    source_endpoint_id: str = "$.input.transfer_source_endpoint_id"
    destination_endpoint_id: str = "$.input.transfer_destination_endpoint_id"
    transfer_items: t.Union[t.List[TransferItem], str] = [TransferItem()]
    notify_on_succeeded: t.Optional[t.Union[bool, str]] = None
    notify_on_failed: t.Optional[t.Union[bool, str]] = None
    notify_on_inactive: t.Optional[t.Union[bool, str]] = None


class TransferDelete(ActionState):
    """
    Action Provider state for deleting files from a Globus Collection.

    Example:

    .. code-block:: python

        from gladier import GladierClient
        from gladier.tools import GlobusTransferDelete

        client = GladierClient(flow_definition=GlobusTransferDelete().get_flow_definition())
        flow_run = client.run_flow(
            {"input": {

                "transfer_delete_endpoint_id": "ddb59aef-6d04-11e5-ba46-22000b92c6ec",
                "transfer_delete_items": ["~/godata"],
            }}
        )

    """

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
