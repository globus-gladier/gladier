import globus_sdk
from gladier.tests.test_data.gladier_mocks import MockGladierClient

ALL_FLOW_SCOPES = [
    globus_sdk.FlowsClient.scopes.manage_flows,
    globus_sdk.FlowsClient.scopes.view_flows,
    globus_sdk.FlowsClient.scopes.run,
    globus_sdk.FlowsClient.scopes.run_status,
    globus_sdk.FlowsClient.scopes.run_manage,
]


def test_logged_out(logged_out):
    assert MockGladierClient().is_logged_in() is False


def test_logged_in(logged_in):
    mc = MockGladierClient()
    assert not mc.missing_authorizers
    assert mc.is_logged_in() is True


def test_scopes(logged_in):
    cli = MockGladierClient()
    assert not set(ALL_FLOW_SCOPES).difference(cli.scopes)
