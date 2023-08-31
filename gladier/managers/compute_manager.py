import hashlib
import logging
from packaging.version import parse as parse_version

import gladier.managers.compute_login_manager
from gladier.base import GladierBaseTool
from gladier.managers.service_manager import ServiceManager
from globus_compute_sdk import Client, serialize, version as compute_sdk_version

log = logging.getLogger(__name__)


class ComputeManager(ServiceManager):
    def __init__(self, auto_registration: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.auto_registration = auto_registration

    def get_scopes(self):
        return gladier.managers.compute_login_manager.ComputeLoginManager.SCOPES

    @property
    def compute_client(self):
        """
        :return: an authorized compute client
        """
        if getattr(self, "__compute_client", None) is not None:
            return self.__compute_client

        compute_login_manager = (
            gladier.managers.compute_login_manager.ComputeLoginManager(
                authorizers=self.login_manager.get_manager_authorizers()
            )
        )

        self.__compute_client = Client(
            code_serialization_strategy=self.get_serialization_strategy(),
            login_manager=compute_login_manager,
        )
        return self.__compute_client

    @staticmethod
    def get_compute_function_name(compute_function):
        """
        Generate a function name given a compute function. These function names are used to refer
        to compute functions within the config. There is no guarantee of uniqueness for function
        names.

        :return: human readable string identifier for a function (intended for a gladier.cfg file)
        """
        return f"{compute_function.__name__}_function_id"

    @staticmethod
    def get_serialization_strategy():
        """
        Get serialization strategy for functions in the globus compute SDK. Defaults to serialize.DillCodeSource.
        """
        try:
            return serialize.DillCodeSource()
        except AttributeError:
            # Note, this is being used to support pre-2.3.0 versions which don't have serialize.DillSourceCode.
            # We should drop support for pre-2.3.0 in Gladier v0.10.0 and remove this!
            log.warning(
                'Failed to find default compute strategy "serialize.DillCodeSource()" in version '
                f"(globus_compute_sdk v{compute_sdk_version.__version__}), using compute_sdk defaults instead."
            )
            return None

    @staticmethod
    def get_compute_function_checksum(compute_function):
        """
        Get the SHA256 checksum of a compute function
        :return: sha256 hex string of a given compute function
        """
        # This should only be supported in Gladier v0.10.0
        if parse_version(compute_sdk_version.__version__) < parse_version("2.3.0"):
            log.warning(
                f"Using an older version (v{compute_sdk_version.__version__}) of the globus_compute_sdk "
                "which does not support custom serialization strategies! Please upgrade, this will be removed "
                "in Gladier v0.10.0"
            )
            fxs = serialize.ComputeSerializer()
        else:
            fxs = serialize.ComputeSerializer(
                strategy_code=ComputeManager.get_serialization_strategy()
            )
        serialized_func = fxs.serialize(compute_function).encode()
        return hashlib.sha256(serialized_func).hexdigest()

    def validate_function(self, tool: GladierBaseTool, function):
        fid_name = gladier.utils.name_generation.get_compute_function_name(function)
        fid = self.storage.get_value(fid_name)
        checksum = self.get_compute_function_checksum(function)
        checksum_name = (
            gladier.utils.name_generation.get_compute_function_checksum_name(function)
        )
        try:
            if not fid_name:
                raise gladier.exc.RegistrationException(
                    f"Tool {tool.__class__.__name__} missing compute registration for {fid_name}"
                )
            if not self.storage.get_value(checksum_name):
                raise gladier.exc.RegistrationException(
                    f"Tool {tool.__class__.__name__} with function {fid_name} "
                    f"has a function id but no checksum!"
                )
            if not self.storage.get_value(checksum_name) == checksum:
                raise gladier.exc.FunctionObsolete(
                    f"Tool {tool.__class__.__name__} with function {fid_name} "
                    f"has changed and needs to be re-registered."
                )
        except (gladier.exc.RegistrationException, gladier.exc.FunctionObsolete):
            if self.auto_registration is True:
                log.info(
                    f"{tool.__class__.__name__}: function {function.__name__} is out of date"
                )
                fid = self.register_function(tool, function)
                fx_name = gladier.utils.name_generation.get_compute_function_name(
                    function
                )
                self.storage.set_value(fx_name, fid)
                self.storage.set_value(checksum_name, checksum)
            else:
                raise
        finally:
            return fid_name, fid

    def register_function(self, tool: GladierBaseTool, function):
        """Register the functions with Globus Compute."""
        log.info(f"{tool.__class__.__name__}: registering function {function.__name__}")
        return self.compute_client.register_function(function)
