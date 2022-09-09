import logging
from typing import List, Union, Any

import fair_research_login
from globus_sdk import AccessTokenAuthorizer, RefreshTokenAuthorizer
from gladier.exc import AuthException

log = logging.getLogger(__name__)


class LoginManager:

    def __init__(self, client_id: str, storage: Any, app_name: str):
        self.storage = storage
        self.client_id = client_id
        self.app_name = app_name
        self.required_scopes = set()
        self.scope_changes = set()

    @property
    def missing_authorizers(self) -> List[str]:
        """
        :return:  a list of Globus scopes for which there are no authorizers
        """
        loaded = set(self.get_native_client().get_authorizers_by_scope())
        missing = self.required_scopes.difference(loaded)
        for scope in self.scope_changes:
            missing.add(scope)
        return missing

    def is_logged_in(self) -> bool:
        return not bool(self.missing_authorizers)

    def add_requirements(self, scopes: List[str]):
        log.debug(f'Added required scopes {scopes}')
        self.required_scopes = self.required_scopes | set(scopes)

    def add_scope_change(self, scopes: List[str]):
        """
        A scope change happens when the underlying scope gets updated with new dependent scopes,
        and the current token we now have is invalid and can no longer be used. The solution is
        a new login to get a new token.
        """
        log.debug(f'Tracking scope change: {scopes}')
        self.scope_changes = self.scope_changes | set(scopes)

    def get_authorizers(self) -> List[Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        self.ensure_logged_in()
        return self.get_native_client().get_authorizers_by_scope()

    def ensure_logged_in(self):
        missing = self.missing_authorizers
        if missing:
            log.debug(f'Missing the following scopes requiring a login: {missing}')
            kwargs = {}
            if self.scope_changes:
                kwargs['force'] = True
            self.login(requested_scopes=missing, **kwargs)

    def login(self, **login_kwargs):
        """Login to the Gladier client. This will ensure the user has the correct
        tokens configured but it DOES NOT guarantee they are in the correct group to
        run a flow. Can be run both locally and on a server.
        See help(fair_research_login.NativeClient.login) for a full list of kwargs.
        """
        nc = self.get_native_client()
        # if self.is_logged_in() and login_kwargs.get('force') is not True:
        #     log.debug('Already logged in, skipping login.')
        #     return
        log.info('Initiating Native App Login...')
        log.debug(f'Requesting Scopes: {self.required_scopes}')
        login_kwargs['requested_scopes'] = login_kwargs.get('requested_scopes',
                                                            self.required_scopes)
        login_kwargs['refresh_tokens'] = login_kwargs.get('refresh_tokens', True)
        nc.login(**login_kwargs)
        self.authorizers = nc.get_authorizers_by_scope()

    def logout(self):
        """Log out and revoke this client's tokens. This object will no longer
        be usable until a new login is called.
        """
        log.info(f'Revoking the following scopes: {self.scopes}')
        self.get_native_client().logout()
        # Clear authorizers cache
        self.authorizers = dict()

    def get_native_client(self):
        """
        fair_research_login.NativeClient is used when ``authorizers`` are not provided to __init__.
        This enables local login to the Globus Automate Client, FuncX, and any other Globus
        Resource Server.

        :return: an instance of fair_research_login.NativeClient
        """
        if getattr(self, 'client_id', None) is None:
            raise AuthException(
                'Gladier client must be instantiated with a '
                '"client_id" to use "login()!'
            )
        return fair_research_login.NativeClient(client_id=self.client_id,
                                                app_name=self.app_name,
                                                token_storage=self.storage)
