from globus_automate_client.flows_client import ALL_FLOW_SCOPES

from gladier.tests.test_data.gladier_mocks import MockGladierClient


def test_logged_out(logged_out):
    assert MockGladierClient(auto_login=False).is_logged_in() is False


def test_logged_in(logged_in):
    mc = MockGladierClient()
    assert not mc.missing_authorizers
    assert mc.is_logged_in() is True


def test_scopes(logged_in):
    cli = MockGladierClient()
    assert not set(ALL_FLOW_SCOPES).difference(cli.scopes)
