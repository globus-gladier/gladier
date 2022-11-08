import logging
import hashlib

from gladier.base import GladierBaseTool
from gladier.managers.service_manager import ServiceManager
from funcx import FuncXClient
from funcx.serialize import FuncXSerializer

import gladier.utils.funcx_login_manager

log = logging.getLogger(__name__)


class FuncXManager(ServiceManager):

    def __init__(self, auto_registration: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.auto_registration = auto_registration

    def get_scopes(self):
        return gladier.utils.funcx_login_manager.FuncXLoginManager.SCOPES

    @property
    def funcx_client(self):
        """
        :return: an authorized funcx client
        """
        if getattr(self, '__funcx_client', None) is not None:
            return self.__funcx_client

        funcx_login_manager = gladier.utils.funcx_login_manager.FuncXLoginManager(
            authorizers=self.login_manager.get_manager_authorizers()
        )

        self.__funcx_client = FuncXClient(login_manager=funcx_login_manager)
        return self.__funcx_client

    @staticmethod
    def get_funcx_function_name(funcx_function):
        """
        Generate a function name given a funcx function. These function namse are used to refer
        to funcx functions within the config. There is no guarantee of uniqueness for function
        names.

        :return: human readable string identifier for a function (intended for a gladier.cfg file)
        """
        return f'{funcx_function.__name__}_funcx_id'

    @staticmethod
    def get_funcx_function_checksum(funcx_function):
        """
        Get the SHA256 checksum of a funcx function
        :return: sha256 hex string of a given funcx function
        """
        fxs = FuncXSerializer()
        serialized_func = fxs.serialize(funcx_function).encode()
        return hashlib.sha256(serialized_func).hexdigest()

    def validate_function(self, tool: GladierBaseTool, function):
        fid_name = gladier.utils.name_generation.get_funcx_function_name(function)
        fid = self.storage.get_value(fid_name)
        checksum = self.get_funcx_function_checksum(function)
        checksum_name = gladier.utils.name_generation.get_funcx_function_checksum_name(function)
        try:
            if not fid_name:
                raise gladier.exc.RegistrationException(
                    f'Tool {tool.__class__.__name__} missing funcx registration for {fid_name}')
            if not self.storage.get_value(checksum_name):
                raise gladier.exc.RegistrationException(
                    f'Tool {tool.__class__.__name__} with function {fid_name} '
                    f'has a function id but no checksum!')
            if not self.storage.get_value(checksum_name) == checksum:
                raise gladier.exc.FunctionObsolete(
                    f'Tool {tool.__class__.__name__} with function {fid_name} '
                    f'has changed and needs to be re-registered.')
        except (gladier.exc.RegistrationException, gladier.exc.FunctionObsolete):
            if self.auto_registration is True:
                log.info(f'{tool.__class__.__name__}: function {function.__name__} is out of date')
                fid = self.register_function(tool, function)
                fx_name = gladier.utils.name_generation.get_funcx_function_name(function)
                self.storage.set_value(fx_name, fid)
                self.storage.set_value(checksum_name, checksum)
            else:
                raise
        finally:
            return fid_name, fid

    def register_function(self, tool: GladierBaseTool, function):
        """Register the functions with funcx. Ids are saved in the local gladier.cfg"""
        log.info(f'{tool.__class__.__name__}: registering function {function.__name__}')
        return self.funcx_client.register_function(function)
