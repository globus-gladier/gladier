from gladier import GladierBaseClient
from gladier.tools.globus import GlobusComputeStep, GlobusTransferItem, GlobusTransfer


def mock_func(**kwargs):
    pass


def test_globus_compute_state():
    compute_step = GlobusComputeStep(
        function_to_call=mock_func, function_parameters={"foo": "bar"}
    )

    client = GladierBaseClient(start_at=compute_step)
    flow_def = client.get_flow_definition()

    assert flow_def["StartAt"] == compute_step.valid_state_name
    for action_prop_name in {"ActionUrl", "ResultPath", "Type", "End", "Parameters"}:
        assert action_prop_name in flow_def["States"][compute_step.valid_state_name]


def test_globus_transfer_state():
    transfer_step = GlobusTransfer(
        source_endpoint_id="src",
        destination_endpoint_id="dest",
        transfer_items=[
            GlobusTransferItem(source_path="src_path", destination_path="dest_path")
        ],
    )

    flow_def = transfer_step.get_flow_definition()

    assert (
        flow_def["States"][transfer_step.valid_state_name]["Parameters"][
            "source_endpoint_id"
        ]
        == "src"
    )
    assert (
        flow_def["States"][transfer_step.valid_state_name]["Parameters"][
            "destination_endpoint_id"
        ]
        == "dest"
    )
    assert (
        "transfer_items"
        in flow_def["States"][transfer_step.valid_state_name]["Parameters"]
    )
