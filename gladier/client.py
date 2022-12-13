import os
import logging
import warnings
from typing import Union, Mapping
from collections.abc import Iterable

from gladier.base import GladierBaseTool
from gladier.managers.login_manager import (
    BaseLoginManager, CallbackLoginManager, AutoLoginManager
)
from globus_sdk import AccessTokenAuthorizer, RefreshTokenAuthorizer
from gladier.managers import FlowsManager, FuncXManager

from gladier.storage.tokens import GladierSecretsConfig
from gladier.storage.config import GladierConfig
import gladier
import gladier.storage.config
import gladier.utils.dynamic_imports
import gladier.utils.automate
import gladier.utils.name_generation
import gladier.storage.migrations
import gladier.utils.tool_alias
import gladier.utils.funcx_login_manager
import gladier.exc
import gladier.version
log = logging.getLogger(__name__)


class GladierBaseClient(object):
    """
    The Gladier Client ties together commonly used funcx functions
    and basic flows with auto-registration tools to make complex tasks
    easy to automate.

    This class is intended to be subclassed as follows:

    .. code-block:: python

        @generate_flow_definition
        class MyGladierClient(GladierBaseClient):
            gladier_tools = [MyTool]

    And used like the following:

    .. code-block:: python

        my_gc = MyGladierClient()
        flow = my_gc.run_flow(flow_input={"flow_input": {"my_field": "foo"}})
        run_id = flow["run_id"]
        my_gc.progress(run_id)
        pprint(tar_and_transfer.get_status(run_id))

    The following class variables can be set on clients to change their behavior when
    deploying and running flows.

    * glaider_tools (default: [])
       * A list of Gladier Tools to build a working flow_defitinion. Each tool's minimum input
         must be satisfied prior to running the flow. Can be used with the
         @generate_flow_definition decorator to automatically chain together flow definitions
         present on each tool in linear order.
    * flow_definition (default: {})
       * An explicit flow definition to use for this client. Cannot be used with
         @generate_flow_definition
    * secret_config_filename (default: ``~/.gladier-secrets.cfg``)
       * Storage are for Globus Tokens and general storage
    * app_name (default: 'Gladier Client')
       * The app name used during a login flow
    * client_id
       * The Globus Client ID used for native logins
    * globus_group (default: None)
       * A Globus Group to be applied to all flow/run permissions. Group will automatically be
         added to flow_viewers, flow_starters, flow_administrators, run_managers, run_monitors
    * subscription_id (default: None)
       * The subscription id associated with this flow
    * alias_class (default: gladier.utils.tool_alias.StateSuffixVariablePrefix)
       * The default class used to for applying aliases to Tools

    Default options are intended for CLI usage and maximum user convenience.

    :param auto_registration: Automatically register functions or flows if they are not
                              previously registered or obsolete.
    :param login_manager: Class defining login behavior. Defaults to AutoLoginManager, and
                          will auto-login when additional scopes are needed.
    :param flows_manager: A flows manager class with customized behavior. Attrs like group
                          and login_manager will automatically be set if None
    :raises gladier.exc.AuthException: if authorizers given are insufficient

    """
    secret_config_filename = os.path.expanduser("~/.gladier-secrets.cfg")
    app_name = 'Gladier Client'
    client_id = 'f1631610-d9e4-4db2-81ba-7f93ad4414e3'
    globus_group = None
    subscription_id = None
    alias_class = gladier.utils.tool_alias.StateSuffixVariablePrefix

    def __init__(
        self,
        authorizers: Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]] = None,
        auto_login: bool = True,
        auto_registration: bool = True,
        login_manager: BaseLoginManager = None,
        flows_manager: FlowsManager = None,
            ):

        self._tools = None

        # Setup storage
        section = gladier.utils.name_generation.get_snake_case(self.__class__.__name__)
        self.storage = GladierConfig(self.secret_config_filename, section)
        self.storage.update()

        if auto_login is False:
            warnings.warn('auto_login=False in Gladier clients is deprecated and will '
                          'be removed in v0.8. See '
                          'https://gladier.readthedocs.io/en/latest/gladier/customizing_auth.html',
                          category=DeprecationWarning)
        if authorizers:
            warnings.warn('Calling Gladier clients with "authorizers" is deprecated. Instead, see '
                          'https://gladier.readthedocs.io/en/latest/gladier/customizing_auth.html',
                          category=DeprecationWarning)
            self.login_manager = CallbackLoginManager(authorizers=authorizers)
        elif not login_manager:
            section_name = f'tokens_{self.client_id}'
            token_storage = GladierSecretsConfig(self.secret_config_filename, section_name)
            self.login_manager = AutoLoginManager(self.client_id, token_storage, self.app_name,
                                                  auto_login=auto_login)
        else:
            self.login_manager = login_manager

        self.flows_manager = flows_manager or FlowsManager(auto_registration=auto_registration)
        if self.globus_group:
            self.flows_manager.globus_group = self.globus_group
        if self.subscription_id:
            self.flows_manager.subscription_id = self.subscription_id
        if not self.flows_manager.flow_title:
            self.flows_manager.flow_title = f'{self.__class__.__name__} flow'

        self.funcx_manager = FuncXManager(auto_registration=auto_registration)

        for man in (self.flows_manager, self.funcx_manager):
            man.set_storage(self.storage, replace=False)
            man.set_login_manager(self.login_manager, replace=False)
            man.register_scopes()

    @staticmethod
    def get_gladier_defaults_cls(tool_ref, alias_class=None):
        """
        Load a Gladier default class (gladier.GladierBaseTool) by import string. For
        Example: get_gladier_defaults_cls('gladier.tools.hello_world.HelloWorld')

        :param tool_ref: A tool ref can be a dotted import string or an actual GladierBaseTool
                         class.
        :return: gladier.GladierBaseTool
        """
        log.debug(f'Looking for Gladier tool: {tool_ref} ({type(tool_ref)})')
        if isinstance(tool_ref, str):
            default_cls = gladier.utils.dynamic_imports.import_string(tool_ref)
            _, alias = gladier.utils.dynamic_imports.parse_alias(tool_ref)
            default_inst = default_cls(alias, alias_class)
            if issubclass(type(default_inst), gladier.base.GladierBaseTool):
                return default_inst
            raise gladier.exc.ConfigException(f'{default_inst} is not of type '
                                              f'{gladier.base.GladierBaseTool}')
        elif isinstance(tool_ref, gladier.base.GladierBaseTool):
            return tool_ref
        else:
            cls_inst = tool_ref()
            if isinstance(cls_inst, gladier.base.GladierBaseTool):
                return cls_inst
            raise gladier.exc.ConfigException(
                f'"{tool_ref}" must be a {gladier.base.GladierBaseTool} or a dotted import '
                'string ')

    @property
    def version(self):
        return gladier.version.__version__

    @property
    def tools(self):
        """
        Load the current list of tools configured on this class

        :return: a list of subclassed instances of gladier.GladierBaseTool
        """
        if getattr(self, '_tools', None):
            return self._tools

        if not getattr(self, 'gladier_tools', None) or not isinstance(self.gladier_tools, Iterable):
            raise gladier.exc.ConfigException(
                '"gladier_tools" must be a defined list of Gladier Tools. '
                'Ex: ["gladier.tools.hello_world.HelloWorld"]')
        self._tools = [self.get_gladier_defaults_cls(gt, self.alias_class)
                       for gt in self.gladier_tools]
        return self._tools

    @property
    def scopes(self):
        """
        The current list of scopes required by this class. This changes if there
        is a flow configured in the local Gladier config file, otherwise it will
        only consist of basic scopes for running the funcx client/flows client/etc

        :return: list of globus scopes required by this client
        """
        return list(self.login_manager.get_authorizers().keys())

    @property
    def missing_authorizers(self):
        """
        :return:  a list of Globus scopes for which there are no authorizers
        """
        return self.login_manager.missing_authorizers

    def logout(self):
        """Log out and revoke this client's tokens. This object will no longer
        be usable until a new login is called.
        """
        return self.login_manager.logout()

    def is_logged_in(self):
        """
        Check if the client is logged in.

        :return: True, if there are no self.missing_authorizers. False otherwise.
        """
        return self.login_manager.is_logged_in()

    def get_flow_definition(self):
        """
        Get the flow definition attached to this class. If the flow definition is an import string,
        it will automatically load the import string and return the full flow.

        :return: A dict of the Automate Flow definition
        """
        if not getattr(self, 'flow_definition', None):
            raise gladier.exc.ConfigException(f'"flow_definition" was not set on '
                                              f'{self.__class__.__name__}')

        if isinstance(self.flow_definition, dict):
            return self.flow_definition
        elif isinstance(self.flow_definition, str):
            return self.get_gladier_defaults_cls(self.flow_definition).flow_definition
        raise gladier.exc.ConfigException('"flow_definition" must be a dict or an import string '
                                          'to a sub-class of type '
                                          '"gladier.GladierBaseTool"')

    def sync_flow(self):
        self.flows_manager.flow_definition = self.get_flow_definition()
        self.flows_manager.sync_flow()

    def run_flow(self, flow_input=None, use_defaults=True, **flow_kwargs):
        combine_flow_input = self.get_input() if use_defaults else dict()
        if flow_input is not None:
            if not flow_input.get('input') or len(flow_input.keys()) != 1:
                raise gladier.exc.ConfigException(
                    f'Malformed input to flow, all input must be nested under "input", got '
                    f'{flow_input.keys()}')
            combine_flow_input['input'].update(flow_input['input'])
        for tool in self.tools:
            self.check_input(tool, combine_flow_input)

        self.sync_flow()
        return self.flows_manager.run_flow(flow_input=combine_flow_input, **flow_kwargs)

    def get_funcx_function_ids(self):
        """Get all funcx function ids for this run, registering them if there are no ids
        stored in the local Gladier config file OR the stored function id checksums do
        not match the actual functions provided on each of the Gladier tools. If register
        is False, no changes to the config will be made and exceptions will be raised instead.

        :raises: gladier.exc.RegistrationException
        :raises: gladier.exc.FunctionObsolete
        :returns: a dict of function ids where keys are names and values are funcX function ids.
        """
        funcx_ids = dict()
        for tool in self.tools:
            log.debug(f'Checking functions for {tool}')
            funcx_funcs = getattr(tool, 'funcx_functions', [])
            if not funcx_funcs:
                log.warning(f'Tool {tool} did not define any funcX functions!')
            if not funcx_funcs and not isinstance(funcx_funcs, Iterable):
                raise gladier.exc.DeveloperException(
                    f'Attribute "funcx_functions" on {tool} needs to be an iterable! Found '
                    f'{type(funcx_funcs)}')

            for func in funcx_funcs:
                name, val = self.funcx_manager.validate_function(tool, func)
                funcx_ids[name] = val
        return funcx_ids

    def get_input(self) -> dict:
        """
        Get funcx function ids, funcx endpoints, and each tool's default input. Default
        input may not be enough to run the flow. For example if a tool does processing on a
        local filesystem, the file will always need to be provided by the user when calling
        run_flow().

        Defaults rely on GladierBaseTool.flow_input defined separately for each tool.

        :return: input for a flow wrapped in an 'input' dict. For example:
                 {'input': {'foo': 'bar'}}
        """
        flow_input = self.get_funcx_function_ids()
        for tool in self.tools:
            # conflicts = set(flow_input.keys()).intersection(set(tool.flow_input))
            # if conflicts:
            #     for prev_tools in tools:
            #         for r in prev_tools.flow_input:
            #             if set(flow_input.keys()).intersection(set(tool.flow_input)):
            #                 raise gladier.exc.ConfigException(
            #                   f'Conflict: Tools {tool} and {prev_tool} 'both define {r}')
            flow_input.update(tool.get_flow_input())
            # Iterate over both private and public input variables, and include any relevant ones
            # Note: Precedence starts and ends with: Public --> Private --> Default on Tool
            input_keys = set(tool.get_flow_input()) | set(tool.get_required_input())
            log.debug(f'{tool}: Looking for overrides for the following input keys: {input_keys}')
            override_values = {k: self.storage.get_value(k) for k in input_keys
                               if self.storage.get_value(k) is not None}
            if override_values:
                log.info(f'Updates from {self.storage.filename}: {list(override_values.keys())}')
                flow_input.update(override_values)
        return {'input': flow_input}

    def check_input(self, tool: GladierBaseTool, flow_input: dict):
        """
        Do basic checking on included input against requirements set by a tool. Raises an
        exception if the check does not 'pass'

        :param tool: The gladier.GladierBaseTool tool set in self.tools
        :param flow_input: Flow input intended to be passed to run_flow()
        :raises: gladier.exc.ConfigException
        """
        for req_input in tool.get_required_input():
            if req_input not in flow_input['input']:
                raise gladier.exc.ConfigException(
                    f'{tool} requires flow input value: "{req_input}"')

    def get_status(self, action_id: str):
        """
        Get the current status of the automate flow. Attempts to do additional work on funcx
        functions to deserialize any exception output.

        :param action_id: The globus action UUID used for this flow. The Automate flow id is
                          always the flow_id configured for this tool.
        :raises: Globus Automate exceptions from self.flows_client.flow_action_status
        :returns: a Globus Automate status object (with varying state structures)
        """
        return self.flows_manager.get_status(action_id)

    def progress(self, action_id, callback=None):
        """
        Continuously call self.get_status() until the flow completes. Each status response is
        used as a parameter to the provided callback, by default will use the builtin callback
        to print the current state to stdout.

        :param action_id: The action id for a running flow. The flow is automatically pulled
                          based on the current tool's flow_definition.
        :param callback: The function to call with the result from self.get_status. Must take
                         a single parameter: mycallback(self.get_status())
        """
        return self.flows_manager.progress(action_id, callback=callback)

    def get_details(self, action_id, state_name):
        """
        Attempt to extrapolate details from get_status() for a given state_name define in the flow
        definition. Note: This is usually only possible when a flow completes.

        :param action_id: The action_id for this flow. Flow id is automatically determined based
                          on the current tool being run.
        :param state_name: The state in the automate definition to fetch
        :returns: sub-dict of get_status() describing the :state_name:.
        """
        return gladier.utils.automate.get_details(self.get_status(action_id), state_name)
