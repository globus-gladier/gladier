import logging
import time
import pathlib
from typing import Callable, List, Set, Iterable, Union, Any, Mapping
import typing as t
from collections import defaultdict
from typing_extensions import TypeAlias
import abc
import urllib

import fair_research_login
import globus_sdk
from globus_sdk import (
    AccessTokenAuthorizer,
    RefreshTokenAuthorizer,
    ConfidentialAppAuthClient,
)
from globus_sdk.login_flows import CommandLineLoginFlowManager
from gladier.exc import AuthException
from gladier.storage.tokens import GladierSecretsConfig
import globus_compute_sdk

log = logging.getLogger(__name__)

AUTHORIZER_MAP: TypeAlias = Mapping[
    str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]
]


class BaseLoginManager(abc.ABC):
    def __init__(self, *args, **kwargs):
        self.required_scopes = set()
        self.scope_changes = set()

    @property
    def missing_authorizers(self) -> Set[str]:
        return self.get_missing_authorizers(self.get_authorizers())

    def get_missing_authorizers(
        self,
        authorizers: AUTHORIZER_MAP,
    ) -> Set[str]:
        # Disregard any scopes not in the 'required' list. This allows implementers to return
        # unrelated scopes.
        absent = self.required_scopes.difference(authorizers)
        log.info(
            f"Scopes Absent: {absent or None}, Need Update: {self.scope_changes or None}"
        )
        return absent | self.scope_changes

    def get_manager_authorizers(self) -> AUTHORIZER_MAP:
        """
        Method to be called by any service manager that needs authorizers. Method will guarantee
        live authorizers to the best ability of the current login manager. If missing authorizers
        exist, either because of a scope change or no login has taken place, an exception will be
        raised.
        :returns: a dictionary of authorizers keyed by scope
        :raises gladier.exc.AuthException: If any required scope could not be obtained
        """
        authorizers = self.get_authorizers()
        missing = self.get_missing_authorizers(authorizers)

        if missing:
            log.info("Attempting login to fetch missing authorizers.")
            self.login(missing)
            self.clear_scope_changes()
            authorizers = self.get_authorizers()
            missing = self.get_missing_authorizers(authorizers)

        if missing:
            raise AuthException(
                "Manager Failed to produce "
                f"authorizers for missing scopes: {missing}"
            )
        return authorizers

    @abc.abstractmethod
    def get_authorizers(
        self,
    ) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        """
        This method MUST be implemented by the implementing class.

        Load any existing authorizers and return them to the client. A login *should not* be
        attempted. The Login Manager will determine if the scopes provided are sufficient, and
        automatically call login() they are not.

        Must return a dict where keys are scope strings and values are globus authorizors
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement .get_authorizers()"
        )

    @abc.abstractmethod
    def login(self, scopes: List[str]):
        """
        This method MUST be implemented by the implementing class.

        If this method is called, get_authorizers() has insufficient scopes and requires more
        scopes to continue operations. ``scopes`` MAY reference scopes already saved, which can
        happen if dependent scopes have been added to the scope since last login. For this reason,
        previously saved scopes in this list should be disregarded.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement .ensure_logged_in()"
        )

    def is_logged_in(self) -> bool:
        return not bool(self.missing_authorizers)

    def add_requirements(self, scopes: Iterable[str]):
        log.debug(f"Added required scopes {scopes}")
        self.required_scopes = self.required_scopes | set(scopes)

    def add_scope_change(self, scopes: Iterable[str]):
        """
        A scope change happens when the underlying scope gets updated with new dependent scopes,
        and the current token we now have is invalid and can no longer be used. The solution is
        a new login to get a new token.
        """
        log.debug(f"Tracking scope change: {scopes}")
        self.scope_changes = self.scope_changes | set(scopes)

    def clear_scope_changes(self):
        """
        Clear any tracked scopes that required re-authorhization. This is typically called internally
        after successful login and should not be invoked externally.
        """
        self.scope_changes = set()


class AutoLoginManager(BaseLoginManager):
    """
    Default Login Manager class in Gladier. Automatically initiates a login if any scope
    is missing or needs to be updated.
    """

    refresh_tokens = True

    def __init__(self, client_id: str, storage: Any, app_name: str, auto_login=True):
        super().__init__()
        self.storage = storage
        self.client_id = client_id
        self.app_name = app_name
        self.auto_login = auto_login

    @property
    def native_client(self):
        if getattr(self, "client_id", None) is None:
            raise AuthException(
                "Gladier client must be instantiated with a "
                '"client_id" to use "login()!'
            )
        return fair_research_login.NativeClient(
            client_id=self.client_id, app_name=self.app_name, token_storage=self.storage
        )

    def get_authorizers(
        self,
    ) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        try:
            return self.native_client.get_authorizers_by_scope()
        except fair_research_login.LoadError:
            return dict()

    def login(self, scopes):
        if self.auto_login is False:
            raise AuthException(
                f"Automatic login is disabled. Missing scopes: {scopes}"
            )
        self.native_client.login(
            requested_scopes=scopes, refresh_toknes=self.refresh_tokens, force=True
        )

    def logout(self):
        self.native_client.logout()


class CallbackLoginManager(BaseLoginManager):
    """
    The Callback Login Manager allows for finer grained control of auth within Gladier. Logins
    are lazy up until Gladier attempts to make a call to the Compute service, Flows service, or
    tries to run a flow. Scopes for a deployed flow may be modified at any time, requiring
    a re-login with that flow scope.

    :param authorizers: A dict of autorizers by scope. If these satisfy the login requirements
                        then the callback will not be triggered.
    :param callback: A Callable which will be invoked if additional scopes are needed.

    """

    def __init__(
        self,
        authorizers: Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]],
        callback: Callable = None,
    ):
        super().__init__()
        self.authorizers = authorizers
        self.callback = callback

    def get_authorizers(
        self,
    ) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        return self.authorizers

    def login(self, scopes):
        if not self.callback:
            raise AuthException(
                "New login required for scopes and no callback set on "
                f"login manager: {scopes}"
            )
        new_authorizers = self.callback(scopes)
        self.authorizers.update(new_authorizers)
        log.info("New authorizers have been cached for re-use.")


class ConfidentialClientLoginManager(BaseLoginManager):
    refresh_tokens = True

    def __init__(
        self, client_id: str, client_secret: str, storage: GladierSecretsConfig
    ):
        super().__init__()
        self.storage: GladierSecretsConfig = storage
        self.client_id = client_id
        self.app = ConfidentialAppAuthClient(client_id, client_secret)

    def login(self, scopes: List[str]) -> None:
        log.info("Initiating client credentials grant using client_id and secret")
        response = self.app.oauth2_client_credentials_tokens(requested_scopes=scopes)
        self.storage.write_tokens(response.by_resource_server)

    def by_scopes(self, tokens):
        # Get a flat list of scopes
        scopes = [tset["scope"].split() for tset in tokens.values()]
        scopes = [item for sublist in scopes for item in sublist]

        token_group = {}
        for scope in scopes:
            for tgroup in tokens.values():
                if scope in tgroup["scope"].split():
                    token_group[scope] = tgroup
        return token_group

    def get_authorizers(
        self,
    ) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        tokens = self.storage.read_tokens()
        if not tokens:
            log.info("Tokens failed to load, no tokens in storage.")
            return dict()

        expired = any(t["expires_at_seconds"] < time.time() for t in tokens.values())
        if expired:
            log.info("Tokens Expired, clearing cache")
            self.storage.clear_tokens()
            return dict()

        return {
            scope: RefreshTokenAuthorizer(
                refresh_token=tdata["refresh_token"],
                auth_client=self.app,
                access_token=tdata["access_token"],
                expires_at=tdata["expires_at_seconds"],
            )
            for scope, tdata in self.by_scopes(tokens).items()
        }


class UserAppLoginManager(BaseLoginManager):
    """
    https://globus-sdk-python.readthedocs.io/en/stable/authorization/globus_app/apps.html#globus_sdk.UserApp

    A native Globus SDK implementation of the login manager. Recommended for most users.
    """

    request_refresh_tokens = True

    def __init__(
        self,
        client_id: str,
        app_name: str = "Glaider App",
        globus_auth_parameters: globus_sdk.gare.GlobusAuthorizationParameters = None,
        storage: GladierSecretsConfig = None,
    ):
        super().__init__()
        self.storage = storage
        self.client_id = client_id
        self.app_name = app_name
        self.globus_auth_parameters = (
            globus_auth_parameters or globus_sdk.gare.GlobusAuthorizationParameters()
        )
        self.token_storage = self.get_token_storage()
        self.user_app = globus_sdk.UserApp(
            self.app_name,
            client_id=self.client_id,
            config=globus_sdk.GlobusAppConfig(
                request_refresh_tokens=self.request_refresh_tokens,
                token_storage=self.token_storage,
            ),
        )

    def get_token_storage(self) -> globus_sdk.tokenstorage.TokenStorage:
        """
        Uses Gladier Secrets Config to derive the filenames and sections for the Globus App Token Storage configuraiton.
        """
        storage_filename = pathlib.Path(self.storage.filename)
        filepath = (storage_filename.parent / storage_filename.stem).with_suffix(".db")
        ts = globus_sdk.tokenstorage.SQLiteTokenStorage(
            filepath, namespace=self.storage.section
        )
        log.info(
            f"Using Globus Token Storage: {filepath}, namespace: {self.storage.section}"
        )
        return ts

    def get_token_validation_error_handler(self):
        def token_validation_error_handler(app, error):
            log.warning("Globus App login event!")
            app.login(auth_params=self.globus_auth_parameters)

    def get_authorizers(
        self,
    ) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        """
        Get Authorizers for Gladier, using the mechanisms within a Globus User App.
        """
        # This is a bit unfortunate. The Globus User App doesn't allow us to check what scopes
        # we have saved to disk. We must ask token storage directly for those.
        tokens_by_rs = self.token_storage.get_token_data_by_resource_server()
        # Determine all scopes saved to disk
        scopes = globus_sdk.scopes.scopes_to_scope_list(
            t.scope for t in tokens_by_rs.values()
        )
        tokens_by_scope = {}
        for scope in scopes:
            for tdata in tokens_by_rs.values():
                if str(scope) in tdata.scope.split():
                    tokens_by_scope[str(scope)] = tdata

        # Use the User App to load authorizers for all of the scopes we have. We let the user
        # app do this to handle building the authorizer
        auth_by_scope = {
            str(scope): self.user_app.get_authorizer(tdata.resource_server)
            for scope, tdata in tokens_by_scope.items()
        }
        return auth_by_scope

    def login(self, scopes):
        """
        Integrates the Globus App login flow.
        """
        log.debug(f"User App Login with scopes: {scopes}")
        # This is a bit unfortunate. add_scope_requirements() requires passing scopes
        # by resource server, which we don't readily have available. That means we need
        # to figure out which resource servers correspond to which scopes.
        self.user_app.add_scope_requirements(self.scopes_by_resource_server(scopes))
        self.user_app.login(auth_params=self.globus_auth_parameters)

    def logout(self):
        """
        Initiate a Globus User App logout. Revokes and clears credentials on this user system.
        """
        self.user_app.logout()

    def get_resource_server(self, scope):
        """
        Get the resource server for a given Globus Scope. Used internally to fetch resource
        servers for Service Clients required by Gladier. Only supports fetching resource servers
        for:
            - Flows Client
            - Auth Client
            - Globus Compute Client
            - Deployed Flows

        raises: ValueError if the resource server for the scope cannot be determined.
        """
        services = (globus_sdk.FlowsClient, globus_sdk.AuthClient)
        for service in services:
            rses = [
                getattr(service.scopes, name) for name in service.scopes.scope_names
            ]
            if scope in rses:
                return service.resource_server

        if scope == globus_compute_sdk.Client.FUNCX_SCOPE:
            return "funcx_service"

        rs, name = urllib.parse.urlparse(scope).path.lstrip("/scopes/").split("/")
        if name.startswith("flow_"):
            return rs

        raise ValueError(f"Unable to find resource server for {scope}")

    def scopes_by_resource_server(self, scopes: t.List[str]) -> t.Mapping[str, str]:
        """
        Determine the resource servers for each scope given and return a mapping of resource
        servers to scopes. Used by the Globus App.
        returns: A mapping of resource servers to scopes, such that:
        {
            "rs1": ["scope1"],
            "rs2": ["scope2", "scope3"],
        }
        """
        # Organize scopes by resource server.
        by_rs = defaultdict(list)
        for scope in scopes:
            by_rs[self.get_resource_server(scope)] += [scope]
        return by_rs
