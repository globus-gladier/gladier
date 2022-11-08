import sys
import uuid
import pytest
from unittest.mock import Mock
from gladier.exc import ConfigException
from gladier.managers.flows_manager import FlowsManager
# from gladier.tests.conftest import login_manager
from gladier.tests.test_data.gladier_mocks import MockGladierClient
import gladier


def test_get_group_urn():
    assert FlowsManager.get_globus_urn(str(uuid.uuid4())).startswith('urn:globus:groups:id:')


def test_bad_principal():
    with pytest.raises(gladier.exc.DevelopmentException):
        FlowsManager.get_globus_urn(str(uuid.uuid4()), 'potatoes!')


def test_flow_group():
    fm = FlowsManager(globus_group='my_globus_group')
    assert fm.get_flow_permission('flow_viewers') == ['urn:globus:groups:id:my_globus_group']


def test_bad_flow_permission():
    fm = FlowsManager(globus_group='my_globus_group')
    with pytest.raises(gladier.exc.DevelopmentException):
        fm.get_flow_permission('motatoes!')


@pytest.mark.skipif(sys.version_info < (3, 8), reason='py37 missing key test feature')
def test_flow_subscription_id(auto_login, storage, mock_flows_client):
    fm = FlowsManager(flow_id='myflow', subscription_id='my_sub')
    fm.storage = storage
    fm.flow_definition = {'hello': 'world'}
    fm._flows_client = mock_flows_client
    fm.register_flow()
    assert mock_flows_client.update_flow.called
    assert mock_flows_client.update_flow.call_args.kwargs['subscription_id'] == 'my_sub'


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


def test_exception_on_immediate_flow_failure(logged_in, mock_flows_client, globus_response):
    globus_response.data = {'status': 'FAILED', 'run_id': 'my_run_id', 'details': {
        'description': 'something bad happened'
    }}
    mock_flows_client.run_flow.return_value = globus_response
    cli = MockGladierClient()
    with pytest.raises(ConfigException):
        cli.run_flow()


def test_custom_scope_id(logged_out):
    cli = MockGladierClient(flows_manager=FlowsManager(flow_id='foo'))
    scope = 'https://auth.globus.org/scopes/foo/flow_foo_user'
    assert scope in cli.login_manager.missing_authorizers


def test_dependent_scope_change_run_flow(auto_login, mock_flows_client,
                                         mock_dependent_token_change_error,
                                         monkeypatch):
    mock_flows_client.run_flow.side_effect = mock_dependent_token_change_error
    fm = FlowsManager(flow_id='foo', login_manager=auto_login)
    # Ensure scopes are set, then disable auto_login behavior
    auto_login.get_manager_authorizers()
    auto_login.login = Mock()
    # Neither of these should return anything, we should be totally logged in at this point
    assert not auto_login.scope_changes
    assert not auto_login.missing_authorizers
    assert auto_login.login.call_count == 0

    # Gladier will re-run run_flow after login, so catch the second 'run_flow()'
    with pytest.raises(gladier.exc.AuthException):
        fm.run_flow()
    assert auto_login.scope_changes == {
        'https://auth.globus.org/scopes/foo/flow_foo_user'
    }
    assert auto_login.login.call_count == 1


def test_dependent_scope_change_no_login(logged_in, mock_flows_client,
                                         monkeypatch):
    cli = MockGladierClient(auto_login=False)
    cli.login_manager.login = Mock()
    cli.login_manager.add_scope_change(['foo'])

    with pytest.raises(gladier.exc.AuthException):
        cli.run_flow()


def test_gladier_raises_globus_errors(logged_in, mock_flows_client, mock_globus_api_error,
                                      monkeypatch):
    mock_flows_client.run_flow.side_effect = mock_globus_api_error
    cli = MockGladierClient()

    with pytest.raises(mock_globus_api_error):
        cli.run_flow()


def test_flow_definition_changed(auto_login, storage):
    fm = FlowsManager(flow_id='foo', login_manager=auto_login, flow_definition={'foo': 'bar'})
    fm.storage = storage
    fm.sync_flow()
    assert fm.flow_changed() is False
    fm.flow_definition = {'bar': 'car'}
    assert fm.flow_changed() is True


def test_run_flow_redeploy_on_404(auto_login, storage, mock_flows_client, mock_globus_api_error):
    fm = FlowsManager(flow_definition={'foo': 'bar'}, login_manager=auto_login)
    storage.set_value('flow_id', 'pre_configured_flow')
    mock_globus_api_error.http_status = 404
    mock_flows_client.run_flow.side_effect = mock_globus_api_error
    fm.storage = storage
    with pytest.raises(mock_globus_api_error):
        fm.run_flow()
    # The manager will first attempt to run the flow, which will fail. It will then
    # deploy and attempt to re-run, resulting in the following calls
    assert mock_flows_client.deploy_flow.call_count == 1
    assert mock_flows_client.run_flow.call_count == 2


def test_run_flow_404_on_explicit_flow_id(auto_login, storage, mock_flows_client,
                                          mock_globus_api_error):
    fm = FlowsManager(flow_id='foo', flow_definition={'foo': 'bar'}, login_manager=auto_login)
    mock_globus_api_error.http_status = 404
    mock_flows_client.run_flow.side_effect = mock_globus_api_error
    fm.storage = storage
    with pytest.raises(mock_globus_api_error):
        fm.run_flow()
    # The manager should not attempt to re-deploy on explicitly set flow_ids
    assert mock_flows_client.deploy_flow.call_count == 0
    assert mock_flows_client.run_flow.call_count == 1


def test_register_flow_redeploy_on_404(auto_login, storage, mock_flows_client,
                                       mock_globus_api_error):
    fm = FlowsManager(flow_definition={'foo': 'bar'}, login_manager=auto_login)
    storage.set_value('flow_id', 'pre_configured_flow')
    mock_globus_api_error.http_status = 404
    mock_flows_client.update_flow.side_effect = mock_globus_api_error
    fm.storage = storage
    fm.register_flow()
    assert mock_flows_client.deploy_flow.call_count == 1
    assert mock_flows_client.update_flow.call_count == 1


def test_register_flow_404_on_explicit_flow_id(auto_login, storage, mock_flows_client,
                                               mock_globus_api_error):
    fm = FlowsManager(flow_id='myflow', flow_definition={'foo': 'bar'}, login_manager=auto_login)
    mock_globus_api_error.http_status = 404
    mock_flows_client.update_flow.side_effect = mock_globus_api_error
    fm.storage = storage
    # An error should be raised if an explicitly set flow_id raises a 404
    with pytest.raises(mock_globus_api_error):
        fm.register_flow()


def test_get_status(auto_login, mock_flow_status_active, mock_flows_client, globus_response):
    fm = FlowsManager(flow_id='foo', login_manager=auto_login)
    globus_response.data = mock_flow_status_active
    mock_flows_client.flow_action_status.return_value = globus_response
    fm.get_status('run_id')


def test_progress(auto_login, mock_flow_status_active, mock_flow_status_succeeded,
                  mock_flows_client):
    fm = FlowsManager(flow_id='foo', login_manager=auto_login)

    class GlobusResponse(object):
        _data = [mock_flow_status_active, mock_flow_status_active, mock_flow_status_succeeded]

        @property
        def data(self):
            return self._data.pop(0)
    responses = GlobusResponse()

    mock_flows_client.flow_action_status.return_value = responses
    fm.progress('run_id')
    assert mock_flows_client.flow_action_status.call_count == 3


def test_get_details(auto_login, mock_flow_status_succeeded, mock_flows_client, globus_response):
    fm = FlowsManager(flow_id='foo', login_manager=auto_login)
    globus_response.data = mock_flow_status_succeeded
    mock_flows_client.flow_action_status.return_value = globus_response
    response = fm.get_details('run_id', 'ShellCmd')
    from pprint import pprint
    pprint(response)
    assert 'Hello Custom Storage!' in response['details']['result'][0][1]
