import time
import types
import globus_sdk
import globus_compute_sdk
import pytest
from gladier.managers import CallbackLoginManager
from gladier.managers.login_manager import UserAppLoginManager
from gladier.exc import AuthException
from globus_sdk.token_storage import TokenStorageData


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
        # Resource servers starting with characters found in "/scopes/" must not be mangled
        (
            "https://auth.globus.org/scopes/eec9b274-0c81/flow_eec9b274_user",
            "eec9b274-0c81",
        ),
        ("https://auth.globus.org/scopes/ce5a-0c81/flow_ce5a_user", "ce5a-0c81"),
    ],
)
def test_get_resource_server(scope, resource_server):
    login_manager = _bare_user_app_manager()
    assert login_manager.get_resource_server(str(scope)) == resource_server
    # Scope objects from the SDK are accepted as well as plain strings
    assert login_manager.get_resource_server(scope) == resource_server
    sdk_scope = globus_sdk.scopes.Scope(str(scope))
    assert login_manager.get_resource_server(sdk_scope) == resource_server


def test_get_resource_server_unknown_scope():
    login_manager = _bare_user_app_manager()
    with pytest.raises(ValueError):
        login_manager.get_resource_server(
            "https://auth.globus.org/scopes/abc-123/other"
        )


def test_user_app_logout_without_login(monkeypatch, tmp_path):
    """Tokens loaded from storage, with no login this session, must still be revoked and cleared"""
    revoked = []
    monkeypatch.setattr(
        globus_sdk.NativeAppAuthClient,
        "oauth2_revoke_token",
        lambda self, token, **kwargs: revoked.append(token),
    )
    storage = types.SimpleNamespace(filename=str(tmp_path / "gladier-secrets.cfg"))
    login_manager = UserAppLoginManager("foo", storage=storage)
    scopes = {
        "flows.globus.org": str(globus_sdk.FlowsClient.scopes.run),
        "funcx_service": globus_compute_sdk.Client.FUNCX_SCOPE,
    }
    login_manager.token_storage.store_token_data_by_resource_server(
        {
            rs: TokenStorageData(
                resource_server=rs,
                identity_id="user-id",
                scope=scope,
                access_token=f"access-{rs}",
                refresh_token=f"refresh-{rs}",
                expires_at_seconds=int(time.time()) + 3600,
                token_type="Bearer",
            )
            for rs, scope in scopes.items()
        }
    )

    login_manager.logout()

    assert sorted(revoked) == sorted(
        [f"{kind}-{rs}" for rs in scopes for kind in ("access", "refresh")]
    )
    assert login_manager.token_storage.get_token_data_by_resource_server() == {}
