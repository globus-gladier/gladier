import sys
import pytest
from unittest.mock import Mock
from gladier.tests.test_data.gladier_mocks import MockGladierClient
import gladier


def test_get_input(logged_in):
    assert MockGladierClient().get_input() == {'input': {
        'funcx_endpoint_non_compute': 'my_non_compute_endpoint_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
    }}


def test_get_input_from_aliased_tool(logged_in):

    class MockGladierClientAlias(MockGladierClient):
        gladier_tools = ['gladier.tests.test_data.gladier_mocks.MockToolWithRequirements:MyAlias']

    assert MockGladierClientAlias().get_input() == {'input': {
        'funcx_endpoint_non_compute': 'my_non_compute_endpoint_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        'my_alias_default_var': 'is a thing!',
    }}


def test_get_input_from_priv_config(logged_in, mock_secrets_config):
    cli = MockGladierClient()
    cli.get_cfg(private=True)[cli.section]['funcx_endpoint_non_compute'] = 'new_ep_uuid'
    assert cli.get_input() == {'input': {
        'funcx_endpoint_non_compute': 'new_ep_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        }
    }


def test_get_input_from_pub_config(logged_in, mock_config):
    cli = MockGladierClient()
    cli.get_cfg(private=False)[cli.section]['funcx_endpoint_non_compute'] = 'new_ep_uuid'
    assert cli.get_input() == {'input': {
        'funcx_endpoint_non_compute': 'new_ep_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        }
    }


def test_pub_config_overrides_priv(logged_in, mock_config, mock_secrets_config):
    cli = MockGladierClient()
    cli.get_cfg(private=True)[cli.section]['funcx_endpoint_non_compute'] = 'priv_ep_uuid'
    cli.get_cfg(private=False)[cli.section]['funcx_endpoint_non_compute'] = 'pub_ep_uuid'
    assert cli.get_input() == {'input': {
        'funcx_endpoint_non_compute': 'pub_ep_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        }
    }


def test_run_flow(logged_in):
    cli = MockGladierClient()
    cli.run_flow()


@pytest.mark.skipif(sys.version_info < (3, 8), reason='py37 missing key test feature')
def test_run_flow_with_label(logged_in, mock_flows_client):
    cli = MockGladierClient()
    cli.run_flow(label='my flow')
    # Python 3.7 doesn't support checking kwargs this way. Skip it.
    assert mock_flows_client.run_flow.call_args.kwargs['label'] == 'my flow'


@pytest.mark.skipif(sys.version_info < (3, 8), reason='py37 missing key test feature')
def test_run_flow_with_long_label(logged_in, mock_flows_client):
    cli = MockGladierClient()
    my_label = 'fl' + 'o' * 63
    expected_label = 'fl' + 'o' * 60 + '..'
    assert len(my_label) == 65
    assert len(expected_label) == 64
    cli.run_flow(label=my_label)
    # Python 3.7 doesn't support checking kwargs this way. Skip it.
    assert mock_flows_client.run_flow.call_args.kwargs['label'] == expected_label


def test_dependent_scope_change_run_flow(logged_in, mock_flows_client,
                                         mock_dependent_token_change_error,
                                         monkeypatch):
    mock_flows_client.run_flow.side_effect = mock_dependent_token_change_error
    cli = MockGladierClient()
    cli.login = Mock()

    # Gladier will re-run run_flow after login, so catch the second 'run_flow()'
    with pytest.raises(mock_dependent_token_change_error):
        cli.run_flow()
    assert cli.login.call_count == 1


def test_dependent_scope_change_no_login(logged_in, mock_flows_client,
                                         mock_dependent_token_change_error,
                                         monkeypatch):
    mock_flows_client.run_flow.side_effect = mock_dependent_token_change_error
    cli = MockGladierClient(auto_login=False)
    cli.login = Mock()

    with pytest.raises(gladier.exc.AuthException):
        cli.run_flow()
    assert cli.login.call_count == 0


def test_gladier_raises_globus_errors(logged_in, mock_flows_client, mock_globus_api_error,
                                      monkeypatch):
    mock_flows_client.run_flow.side_effect = mock_globus_api_error
    cli = MockGladierClient()

    with pytest.raises(mock_globus_api_error):
        cli.run_flow()


@pytest.mark.skip
def test_progress():
    pass


@pytest.mark.skip
def test_get_status():
    pass


@pytest.mark.skip
def test_get_details():
    pass
