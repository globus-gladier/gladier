from __future__ import annotations

import logging
import globus_sdk
from globus_sdk.scopes import AuthScopes
from globus_compute_sdk.sdk.web_client import WebClient
from globus_compute_sdk import Client

log = logging.getLogger(__name__)


class ComputeLoginManager:
    """
    Implements the globus_compute_sdk.sdk.login_manager.protocol.LoginManagerProtocol class.

    https://github.com/funcx-faas/funcX/blob/main/compute_sdk/globus_compute_sdk/sdk/login_manager/protocol.py  # noqa
    """

    SCOPES = [
        Client.FUNCX_SCOPE,
        AuthScopes.openid,
    ]

    def __init__(self, authorizers: dict[str, globus_sdk.RefreshTokenAuthorizer]):
        self.authorizers = authorizers

    def get_auth_client(self) -> globus_sdk.AuthClient:
        return globus_sdk.AuthClient(authorizer=self.authorizers[AuthScopes.openid])

    def get_web_client(
        self, *, base_url: str | None = None, app_name: str | None = None
    ) -> WebClient:
        return WebClient(
            base_url=base_url,
            app_name=app_name,
            authorizer=self.authorizers[Client.FUNCX_SCOPE],
        )

    def ensure_logged_in(self):
        log.warning("ensure_logged_in cannot be invoked from here!")

    def logout(self):
        log.warning("logout cannot be invoked from here!")
