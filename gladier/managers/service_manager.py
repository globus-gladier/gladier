
import logging
from typing import List
import abc
from gladier.managers.login_manager import BaseLoginManager
from gladier.storage.config import GladierConfig


log = logging.getLogger(__name__)


class ServiceManager(abc.ABC):

    def __init__(self, **kwargs):
        self.storage = kwargs.get('storage')

        self.login_manager = kwargs.get('login_manager')
        if self.login_manager is not None:
            self.login_manager.add_requirements(self.get_scopes())

    def set_storage(self, storage: GladierConfig, replace: bool = True) -> None:
        if replace:
            log.info(f'Replacing storage {self.storage} with {storage}')
            self.storage = storage
        else:
            self.storage = self.storage or storage
        log.debug(f'Storage for {self} set to {self.storage}')

    def set_login_manager(self, login_manager: BaseLoginManager, replace: bool = True) -> None:
        if replace:
            log.info(f'Replacing login manager {self.login_manager} with {login_manager}')
            self.login_manager = login_manager
        else:
            self.login_manager = self.login_manager or login_manager
        self.login_manager.add_requirements(self.get_scopes())
        log.debug(f'Login Manager for {self} set to {self.login_manager}')

    def get_scopes() -> List[str]:
        raise NotImplementedError('Service Managers must define their own scope needs')
