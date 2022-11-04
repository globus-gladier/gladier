
import logging
from typing import List
import abc
from gladier.managers.login_manager import BaseLoginManager
from gladier.storage.config import GladierConfig


log = logging.getLogger(__name__)


class ServiceManager(abc.ABC):

    def __init__(self, **kwargs):
        self._storage = kwargs.get('storage')

        self.login_manager = kwargs.get('login_manager')
        self.register_scopes()

    @property
    def storage(self):
        if self._storage is None:
            raise AttributeError(f'Storage has not been set for {self}')
        return self._storage

    @storage.setter
    def storage(self, value):
        self.set_storage(value)

    def set_storage(self, storage: GladierConfig, replace: bool = True) -> None:
        if replace:
            log.info(f'Replacing storage {self._storage} with {storage}')
            self._storage = storage
        else:
            self._storage = self._storage or storage
        log.debug(f'Storage for {self} set to {self._storage}')

    def set_login_manager(self, login_manager: BaseLoginManager, replace: bool = True) -> None:
        if replace:
            log.info(f'Replacing login manager {self.login_manager} with {login_manager}')
            self.login_manager = login_manager
        else:
            self.login_manager = self.login_manager or login_manager
        self.login_manager.add_requirements(self.get_scopes())
        log.debug(f'Login Manager for {self} set to {self.login_manager}')

    def register_scopes(self):
        """
        Register scopes returned by `get_scopes()` with the login manager"""
        if self.login_manager is not None:
            self.login_manager.add_requirements(self.get_scopes())

    def get_scopes() -> List[str]:
        raise NotImplementedError('Service Managers must define their own scope needs')
