import logging
from typing import Callable, List, Set, Iterable, Union, Any, Mapping
import abc

import fair_research_login
from globus_sdk import AccessTokenAuthorizer, RefreshTokenAuthorizer
from gladier.exc import AuthException

log = logging.getLogger(__name__)


class BaseLoginManager(abc.ABC):

    def __init__(self, *args, **kwargs):
        self.required_scopes = set()
        self.scope_changes = set()

    @property
    def missing_authorizers(self) -> Set[str]:
        return self.get_missing_authorizers(self.get_authorizers())

    def get_missing_authorizers(
        self,
        authorizers: Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]
            ) -> Set[str]:
        # Disregard any scopes not in the 'required' list. This allows implementers to return
        # unrelated scopes.
        absent = self.required_scopes.difference(authorizers)
        log.info(f'Scopes Absent: {absent or None}, Need Update: {self.scope_changes or None}')
        return absent | self.scope_changes

    def get_manager_authorizers(self):
        authorizers = self.get_authorizers()
        missing = self.get_missing_authorizers(authorizers)

        if missing:
            log.info('Attempting login to fetch missing authorizers.')
            self.login(missing)
            authorizers = self.get_authorizers()
            missing = self.get_missing_authorizers(authorizers)

        if missing:
            raise AuthException('Manager Failed to produce '
                                f'authorizers for missing scopes: {missing}')
        return authorizers

    @abc.abstractmethod
    def get_authorizers(self) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        """
        This method MUST be implemented by the implementing class.

        Load any existing authorizers and return them to the client. A login *should not* be
        attempted. The Login Manager will determine if the scopes provided are sufficient, and
        automatically call login() they are not.
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement .get_authorizers()')

    @abc.abstractmethod
    def login(self, scopes: List[str]):
        """
        This method MUST be implemented by the implementing class.

        If this method is called, get_authorizers() has insufficient scopes and requires more
        scopes to continue operations. ``scopes`` MAY reference scopes already saved, which can
        happen if dependent scopes have been added to the scope since last login. For this reason,
        previously saved scopes in this list should be disregarded.
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement .ensure_logged_in()')

    def is_logged_in(self) -> bool:
        return not bool(self.missing_authorizers)

    def add_requirements(self, scopes: Iterable[str]):
        log.debug(f'Added required scopes {scopes}')
        self.required_scopes = self.required_scopes | set(scopes)

    def add_scope_change(self, scopes: Iterable[str]):
        """
        A scope change happens when the underlying scope gets updated with new dependent scopes,
        and the current token we now have is invalid and can no longer be used. The solution is
        a new login to get a new token.
        """
        log.debug(f'Tracking scope change: {scopes}')
        self.scope_changes = self.scope_changes | set(scopes)


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
        if getattr(self, 'client_id', None) is None:
            raise AuthException(
                'Gladier client must be instantiated with a '
                '"client_id" to use "login()!'
            )
        return fair_research_login.NativeClient(client_id=self.client_id,
                                                app_name=self.app_name,
                                                token_storage=self.storage)

    def get_authorizers(self) -> List[Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        try:
            return self.native_client.get_authorizers_by_scope()
        except fair_research_login.LoadError:
            return dict()

    def login(self, scopes):
        if self.auto_login is False:
            raise AuthException(f'Automatic login is disabled. Missing scopes: {scopes}')
        self.native_client.login(requested_scopes=scopes,
                                 refresh_toknes=self.refresh_tokens,
                                 force=True)

    def logout(self):
        self.native_client.logout()


class CallbackLoginManager(BaseLoginManager):
    """
    The Callback Login Manager allows for finer grained control of auth within Gladier. Logins
    are lazy up until Gladier attempts to make a call to the FuncX service, Flows service, or
    tries to run a flow. Scopes for a deployed flow may be modified at any time, requiring
    a re-login with that flow scope.

    :param authorizers: A dict of autorizers by scope. If these satisfy the login requirements
                        then the callback will not be triggered.
    :param callback: A Callable which will be invoked if additional scopes are needed.

    """

    def __init__(
        self,
        authorizers: Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]],
        callback: Callable = None
    ):
        super().__init__()
        self.authorizers = authorizers
        self.callback = callback

    def get_authorizers(self) -> List[Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        return self.authorizers

    def login(self, scopes):
        if not self.callback:
            raise AuthException('New login required for scopes and no callback set on '
                                f'login manager: {scopes}')
        new_authorizers = self.callback(scopes)
        self.authorizers.update(new_authorizers)
        log.info('New authorizers have been cached for re-use.')
