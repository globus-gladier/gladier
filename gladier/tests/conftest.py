import os
import json
from unittest.mock import Mock, PropertyMock
import pytest
import fair_research_login
import globus_sdk

from globus_automate_client import flows_client
from gladier.tests.test_data.gladier_mocks import mock_automate_flow_scope
from gladier import GladierBaseClient, config, version

data_dir = os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture(autouse=True)
def mock_login(monkeypatch):
    """Unit tests should never need to call login() or logout(), as doing so
    would use real developer credentials"""
    monkeypatch.setattr(fair_research_login.NativeClient, 'login', Mock())
    monkeypatch.setattr(fair_research_login.NativeClient, 'logout', Mock())
    return fair_research_login.NativeClient


@pytest.fixture
def two_step_flow():
    with open(os.path.join(data_dir, 'two_step_flow.json')) as f:
        return json.loads(f.read())


@pytest.fixture
def mock_version_030(monkeypatch):
    monkeypatch.setattr(version, '__version__', '0.3.0')
    return version.__version__


@pytest.fixture
def mock_version_040(monkeypatch):
    monkeypatch.setattr(version, '__version__', '0.4.0a1')
    return version.__version__


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    monkeypatch.setattr(config.GladierSecretsConfig, 'save', Mock())
    monkeypatch.setattr(config.GladierSecretsConfig, 'read', Mock())
    cfg = config.GladierSecretsConfig('mock_filename', 'section', 'client_id')
    monkeypatch.setattr(GladierBaseClient, '_load_private_config', Mock(return_value=cfg))
    return cfg


@pytest.fixture(autouse=True)
def mock_secrets_config(monkeypatch):
    monkeypatch.setattr(config.GladierSecretsConfig, 'save', Mock())
    return config.GladierSecretsConfig


@pytest.fixture(autouse=True)
def mock_flows_client(monkeypatch, globus_response):
    """Ensure there are no calls out to the Globus Automate Client"""
    mock_flows_cli = Mock()
    mock_flows_cli.deploy_flow.return_value = globus_response(mock_data={
        'id': 'mock_flow_id',
        'globus_auth_scope': mock_automate_flow_scope,
    })
    mock_flows_cli.run_flow.return_value = globus_response(mock_data={
        'action_id': 'mock_flow_id',
        'status': 'ACTIVE',
    })
    monkeypatch.setattr(GladierBaseClient, 'flows_client',
                        PropertyMock(return_value=mock_flows_cli))
    return mock_flows_cli


@pytest.fixture(autouse=True)
def mock_funcx_client(monkeypatch):
    """Ensure there are no calls out to the Funcx Client"""
    mock_fx_cli = Mock()
    mock_fx_cli.register_function.return_value = 'mock_funcx_id'
    monkeypatch.setattr(GladierBaseClient, 'funcx_client',
                        PropertyMock(return_value=mock_fx_cli))
    return mock_fx_cli


@pytest.fixture
def logged_out(monkeypatch):
    load = Mock(side_effect=fair_research_login.LoadError())
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens_by_scope', load)
    return fair_research_login.NativeClient


@pytest.fixture
def logged_in(monkeypatch):
    scopes = list(flows_client.ALL_FLOW_SCOPES) + [
        # Funcx Scope
        'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all',
        # Required by FuncX
        'urn:globus:auth:scope:search.api.globus.org:all', 'openid',
        # The scope we got back from 'deploying' a flow with automate (of course, this is a mock)
        mock_automate_flow_scope,
    ]
    mock_tokens = {
        scope: dict(access_token=f'{scope}_access_token')
        for scope in scopes
    }
    load = Mock(return_value=mock_tokens)
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens_by_scope', load)
    return fair_research_login.NativeClient


@pytest.fixture
def globus_response():
    class GlobusResponse(object):
        def __init__(self, *args, mock_data=None, **kwargs):
            self.data = mock_data
    return GlobusResponse


@pytest.fixture
def mock_globus_api_error(monkeypatch):
    class MockGlobusAPIError(Exception):
        http_status = 400
        code = 'Error'
        message = json.dumps(
            {'error': {
                'code': 'FLOW_GENERIC_ERROR',
                'detail': 'Something terrible happened, and its your fault.'
                }
             })
    monkeypatch.setattr(globus_sdk.exc, 'GlobusAPIError', MockGlobusAPIError)
    return globus_sdk.exc.GlobusAPIError


@pytest.fixture
def mock_dependent_token_change_error(mock_globus_api_error):
    # Yes, this is a real Globus automate exception message...
    automate_message = json.dumps(
        {'error': {'code': 'FLOW_INPUT_ERROR',
                   'detail': 'For RunAs value User, unable to get tokens for scopes '
                   "{'https://auth.globus.org/scopes/actions.globus.org/transfer/transfer'}"
                   }
         })
    mock_globus_api_error.message = automate_message
    return mock_globus_api_error
