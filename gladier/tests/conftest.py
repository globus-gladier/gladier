from unittest.mock import Mock, PropertyMock
import pytest
import uuid
import fair_research_login
import globus_sdk

from globus_automate_client import flows_client
from gladier.tests.test_data.gladier_mocks import mock_automate_flow_scope
from gladier import GladierBaseClient, config


@pytest.fixture(autouse=True)
def mock_login(monkeypatch):
    """Unit tests should never need to call login() or logout(), as doing so
    would use real developer credentials"""
    monkeypatch.setattr(fair_research_login.NativeClient, 'login', Mock())
    monkeypatch.setattr(fair_research_login.NativeClient, 'logout', Mock())
    return fair_research_login.NativeClient


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    monkeypatch.setattr(config.GladierConfig, 'save', Mock())
    return config.GladierConfig


@pytest.fixture(autouse=True)
def mock_flows_client(monkeypatch, globus_response):
    """Ensure there are no calls out to the Globus Automate Client"""
    mock_flows_cli = Mock()
    mock_flows_cli.deploy_flow.return_value = globus_response(mock_data={
        'id': str(uuid.uuid4()),
        'globus_auth_scope': mock_automate_flow_scope,
    })
    mock_flows_cli.run_flow.return_value = globus_response(mock_data={
        'action_id': str(uuid.uuid4()),
        'status': 'ACTIVE',
    })
    monkeypatch.setattr(GladierBaseClient, 'flows_client',
                        PropertyMock(return_value=mock_flows_cli))
    return mock_flows_cli


@pytest.fixture(autouse=True)
def mock_funcx_client(monkeypatch):
    """Ensure there are no calls out to the Funcx Client"""
    mock_fx_cli = Mock()
    mock_fx_cli.register_function.return_value = str(uuid.uuid4())
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
        pass
    monkeypatch.setattr(globus_sdk, 'GlobusAPIError', MockGlobusAPIError)
    return globus_sdk.GlobusAPIError
