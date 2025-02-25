import os
import copy
import json
import configparser
from unittest.mock import Mock, PropertyMock
import pytest
import fair_research_login
from gladier.storage import config, tokens
import globus_sdk

from gladier.tests.test_data.gladier_mocks import mock_automate_flow_scope
from gladier.managers import ComputeManager
from gladier.managers.login_manager import CallbackLoginManager, UserAppLoginManager
from gladier import GladierClient

data_dir = os.path.join(os.path.dirname(__file__), "test_data")

ALL_FLOW_SCOPES = [
    globus_sdk.FlowsClient.scopes.manage_flows,
    globus_sdk.FlowsClient.scopes.view_flows,
    globus_sdk.FlowsClient.scopes.run,
    globus_sdk.FlowsClient.scopes.run_status,
    globus_sdk.FlowsClient.scopes.run_manage,
]


@pytest.fixture(autouse=True)
def mock_login(monkeypatch):
    """Unit tests should never need to call login() or logout(), as doing so
    would use real developer credentials"""
    monkeypatch.setattr(fair_research_login.NativeClient, "login", Mock())
    monkeypatch.setattr(fair_research_login.NativeClient, "logout", Mock())
    return fair_research_login.NativeClient


@pytest.fixture
def two_step_flow():
    with open(os.path.join(data_dir, "two_step_flow.json")) as f:
        return json.loads(f.read())


@pytest.fixture(autouse=True)
def storage(monkeypatch):
    class MemStorage:
        def __init__(self):
            self.data = {}

    storage = MemStorage()

    def read(self, filename=None):
        self.read_dict(storage.data)

    def write(self, cfg=None):
        storage.data = dict(self)

    def save(self):
        self.write()

    monkeypatch.setattr(configparser.ConfigParser, "write", write)
    monkeypatch.setattr(configparser.ConfigParser, "read", read)
    monkeypatch.setattr(config.GladierConfig, "save", save)
    monkeypatch.setattr(tokens.GladierSecretsConfig, "save", save)
    cfg = tokens.GladierSecretsConfig("mock_filename", "tokens_client_id")

    return cfg


@pytest.fixture(autouse=True)
def mock_secrets_config(monkeypatch):
    monkeypatch.setattr(tokens.GladierSecretsConfig, "save", Mock())
    return tokens.GladierSecretsConfig


@pytest.fixture(autouse=True)
def mock_flows_client(monkeypatch, globus_response):
    """Ensure there are no calls out to the Globus Automate Client"""
    mock_create_flow = Mock(
        return_value=globus_response(
            mock_data={
                "id": "mock_flow_id",
                "globus_auth_scope": mock_automate_flow_scope,
            }
        )
    )
    mock_update_flow = Mock(
        return_value=globus_response(
            mock_data={
                "id": "mock_flow_id",
            }
        )
    )
    mock_get_run = Mock(
        return_value=globus_response(
            mock_data={
                "id": "mock_flow_id",
            }
        )
    )

    monkeypatch.setattr(globus_sdk.FlowsClient, "create_flow", mock_create_flow)
    monkeypatch.setattr(globus_sdk.FlowsClient, "update_flow", mock_update_flow)
    monkeypatch.setattr(globus_sdk.FlowsClient, "get_run", mock_update_flow)
    return globus_sdk.FlowsClient


@pytest.fixture(autouse=True)
def mock_specific_flow_client(monkeypatch, globus_response):
    """Ensure there are no calls out to the Globus Automate Client"""
    mock_run_flow = Mock(
        return_value=globus_response(
            mock_data={
                "run_id": "mock_flow_id",
                "status": "ACTIVE",
            }
        )
    )
    monkeypatch.setattr(globus_sdk.SpecificFlowClient, "run_flow", mock_run_flow)
    return globus_sdk.SpecificFlowClient


@pytest.fixture(autouse=True)
def mock_compute_client(monkeypatch):
    """Ensure there are no calls out to the Compute Client"""
    mock_compute_cli = Mock()
    mock_compute_cli.register_function.return_value = "mock_compute_function"
    monkeypatch.setattr(
        ComputeManager, "compute_client", PropertyMock(return_value=mock_compute_cli)
    )
    return mock_compute_cli


@pytest.fixture
def logged_out():
    return CallbackLoginManager({})


@pytest.fixture
def logged_in_tokens():
    scopes = ALL_FLOW_SCOPES + [
        # Compute Scope
        "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
        # Required by Compute
        "openid",
        # The scope we got back from 'deploying' a flow with automate (of course, this is a mock)
        mock_automate_flow_scope,
    ]
    return {scope: dict(access_token=f"{scope}_access_token") for scope in scopes}


@pytest.fixture
def logged_in(monkeypatch, auto_login):
    return auto_login


@pytest.fixture
def auto_login(logged_in_tokens):
    clm = CallbackLoginManager(
        logged_in_tokens,
        lambda scopes: {
            scope: globus_sdk.AccessTokenAuthorizer(scope) for scope in scopes
        },
    )
    return clm


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
        code = "Error"
        message = ""
        text = json.dumps(
            {
                "error": {
                    "code": "FLOW_GENERIC_ERROR",
                    "detail": "Something terrible happened, and its your fault.",
                }
            }
        )

    monkeypatch.setattr(globus_sdk.exc, "GlobusAPIError", MockGlobusAPIError)
    return globus_sdk.exc.GlobusAPIError


@pytest.fixture
def mock_dependent_token_change_error(mock_globus_api_error):
    # Dependent token change error happens when APs are added to a flow.
    automate_message = json.dumps(
        {
            "error": {
                "code": "FLOW_INPUT_ERROR",
                "detail": "For RunAs value User, unable to get tokens for scopes "
                "{'https://auth.globus.org/scopes/actions.globus.org/transfer/transfer'}",
            }
        }
    )
    mock_globus_api_error.text = automate_message
    return mock_globus_api_error


@pytest.fixture
def mock_flow_status_active():
    return {
        "action_id": "c1171657-704c-4537-896f-fcd5bad9062e",
        "details": {
            "code": "FlowStarting",
            "description": "The Flow is starting execution",
            "details": {
                "input": {
                    "input": {
                        "args": "echo 'Hello Custom Storage!'",
                        "capture_output": True,
                        "compute_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
                        "shell_cmd_compute_id": "60e8a10f-524b-4fe0-b125-87b243cee189",
                    }
                }
            },
        },
        "display_status": "ACTIVE",
        "flow_id": "7f324d68-3c50-4c14-b117-1aa0b30aea84",
        "flow_title": "FlowsManager Flow",
        "run_id": "c1171657-704c-4537-896f-fcd5bad9062e",
        "start_time": "2022-11-04T17:20:10.721324+00:00",
        "status": "ACTIVE",
        "user_role": "run_owner",
    }


@pytest.fixture
def mock_flow_status_succeeded(mock_flow_status_active):
    status = copy.deepcopy(mock_flow_status_active)
    status["details"] = {
        "code": "FlowSucceeded",
        "description": "The Flow run reached a successful completion " "state",
        "output": {
            "ShellCmd": {
                "action_id": "f726607a-bd56-4d7b-b3e1-d431df5292ec",
                "details": {"result": [[0, "Hello Custom " "Storage!\n", ""]]},
                "display_status": "Function Results " "Received",
                "state_name": "ShellCmd",
                "status": "SUCCEEDED",
            },
            "input": {
                "args": "echo 'Hello Custom Storage!'",
                "capture_output": True,
                "compute_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
                "shell_cmd_function_id": "60e8a10f-524b-4fe0-b125-87b243cee189",
            },
        },
    }
    for item in ["status", "display_status"]:
        status[item] = "SUCCEEDED"
    return status
