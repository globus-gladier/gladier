import globus_sdk
import globus_compute_sdk
import pytest
from gladier.managers import CallbackLoginManager
from gladier.managers.login_manager import UserAppLoginManager
from gladier.exc import AuthException


def test_callback_manager_login():
    clm = CallbackLoginManager({}, callback=lambda x: {y: {} for y in x})
    clm.login(["foo", "bar"])
    assert list(clm.get_authorizers()) == ["foo", "bar"]


def test_callback_manager_no_callback_set():
    with pytest.raises(AuthException):
        CallbackLoginManager({}, callback=None).login(["foo"])


def _bare_user_app_manager():
    # get_resource_server uses no instance state; skip __init__ to avoid token storage setup
    return UserAppLoginManager.__new__(UserAppLoginManager)


@pytest.mark.parametrize(
    "scope, resource_server",
    [
        (globus_sdk.FlowsClient.scopes.run, "flows.globus.org"),
        (globus_sdk.FlowsClient.scopes.all, "flows.globus.org"),
        (globus_sdk.AuthClient.scopes.openid, "auth.globus.org"),
        (globus_compute_sdk.Client.FUNCX_SCOPE, "funcx_service"),
        ("https://auth.globus.org/scopes/abc-123/flow_abc_123_user", "abc-123"),
    ],
)
def test_get_resource_server(scope, resource_server):
    login_manager = _bare_user_app_manager()
    assert login_manager.get_resource_server(str(scope)) == resource_server
    # Scope objects from the SDK are accepted as well as plain strings
    assert login_manager.get_resource_server(scope) == resource_server


def test_get_resource_server_unknown_scope():
    login_manager = _bare_user_app_manager()
    with pytest.raises(ValueError):
        login_manager.get_resource_server(
            "https://auth.globus.org/scopes/abc-123/other"
        )
