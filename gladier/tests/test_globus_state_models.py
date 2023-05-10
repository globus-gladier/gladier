from gladier import GladierBaseClient
from gladier.tools.globus import GlobusComputeStep


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
