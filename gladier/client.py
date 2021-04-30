import os
import logging
import hashlib
import re
import json
from collections.abc import Iterable

import fair_research_login
import globus_sdk
import globus_automate_client
from funcx import FuncXClient
from funcx.serialize import FuncXSerializer

import gladier
import gladier.config
import gladier.utils.dynamic_imports
import gladier.utils.automate
import gladier.exc
import gladier.version
log = logging.getLogger(__name__)


class GladierBaseClient(object):
    """The Gladier Client ties together commonly used funcx functions
    and basic flows with auto-registration tools to make complex tasks
    easy to automate.

    Default options are intended for CLI usage and maximum user convenience.

    :param authorizers: Provide live globus_sdk authorizers with a dict keyed by
                        scope.
    :type globus_sdk.AccessTokenAuthorizer: A globus authorizer
    :param auto_login: Automatically trigger login() calls when needed. Should not be used
                       with authorizers.
    :param auto_registration: Automatically register functions or flows if they are not
                              previously registered or obsolete.
    :raises gladier.exc.AuthException: if authorizers given are insufficient

    """
    secret_config_filename = os.path.expanduser("~/.gladier-secrets.cfg")
    config_filename = 'gladier.cfg'
    app_name = 'gladier_client'
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'

    def __init__(self, authorizers=None, auto_login=True, auto_registration=True):
        self.__config = None
        self.__flows_client = None
        self.__tools = None
        self.authorizers = authorizers or dict()
        self.auto_login = auto_login
        self.auto_registration = auto_registration
        if self.authorizers and self.auto_login:
            log.warning('Authorizers provided when "auto_login=True", you probably want to set '
                        'auto_login=False if you are providing your own authorizers...')
        if self.authorizers and self.missing_authorizers:
            raise gladier.exc.AuthException(f'Missing Authorizers: {self.missing_authorizers}')
        try:
            if not self.authorizers:
                log.debug('No authorizers provided, loading from disk.')
                self.authorizers = self.get_native_client().get_authorizers_by_scope()
        except fair_research_login.exc.LoadError:
            log.debug('Load from disk failed, login will be required.')
        if self.auto_login and not self.is_logged_in():
            self.login()

    @staticmethod
    def get_gladier_defaults_cls(import_string):
        """
        Load a Gladier default class (gladier.GladierBaseTool) by import string. For
        Example: get_gladier_defaults_cls('gladier.tools.hello_world.HelloWorld')

        :param import_string: A dotted string to the class to import
        :return: gladier.GladierBaseTool
        """
        default_cls = gladier.utils.dynamic_imports.import_string(import_string)
        default_inst = default_cls()
        if isinstance(default_inst, gladier.base.GladierBaseTool):
            return default_inst
        raise gladier.exc.ConfigException(f'"{import_string}" must be a dict '
                                          f'or a dotted import string ')

    @property
    def version(self):
        return gladier.version.__version__

    @property
    def config(self):
        """
        Get the Gladier Config, set by ``self.config_filename``

        :return: The current local Gladier config, configparser.ConfigParser
        """
        if self.__config is not None:
            return self.__config
        self.__config = gladier.config.GladierConfig(filename=self.config_filename)
        return self.__config

    @property
    def gconfig(self):
        """
        Each Gladier Client has its own section in the local Gladier Config.

        :return: the current config section (self.section) for this Gladier client
        """
        return self.config[self.section]

    @property
    def section(self):
        """Get the default section name for the config. The section name is derived
        from the name of the user's flow_definition class turned snake case."""
        name = self.__class__.__name__
        # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
        snake_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        snake_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_name).lower()

        if snake_name not in self.config.sections():
            log.debug(f'Adding new section {snake_name}')
            self.config[snake_name] = {}
        return snake_name

    @property
    def tools(self):
        """
        Load the current list of tools configured on this class

        :return: a list of subclassed instances of gladier.GladierBaseTool
        """
        if getattr(self, '__tools', None):
            return self.__tools

        if not getattr(self, 'gladier_tools', None) or not isinstance(self.gladier_tools, Iterable):
            raise gladier.exc.ConfigException(
                '"gladier_tools" must be a defined list of Gladier Tools. '
                'Ex: ["gladier.tools.hello_world.HelloWorld"]')
        self.__tools = [self.get_gladier_defaults_cls(gt) for gt in self.gladier_tools]
        return self.__tools

    def get_native_client(self):
        """
        fair_research_login.NativeClient is used when ``authorizers`` are not provided to __init__.
        This enables local login to the Globus Automate Client, FuncX, and any other Globus
        Resource Server.

        :return: an instance of fair_research_login.NativeClient
        """
        if getattr(self, 'client_id', None) is None:
            raise gladier.exc.AuthException(
                'Gladier client must be instantiated with a '
                '"client_id" to use "login()!'
            )
        secrets_cfg = fair_research_login.ConfigParserTokenStorage(
            filename=self.secret_config_filename
        )
        return fair_research_login.NativeClient(client_id=self.client_id,
                                                app_name=self.app_name,
                                                token_storage=secrets_cfg)

    @property
    def scopes(self):
        """
        The current list of scopes required by this class. This changes if there
        is a flow configured in the local Gladier config file, otherwise it will
        only consist of basic scopes for running the funcx client/flows client/etc

        :return: list of globus scopes required by this client
        """

        gladier_scopes = list(globus_automate_client.flows_client.ALL_FLOW_SCOPES)
        # Set to funcx_scope = FuncXClient.FUNCX_SCOPE in funcx==0.0.6
        gladier_scopes.append('https://auth.globus.org/scopes/'
                              'facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all')
        flow_scope = self.config[self.section].get('flow_scope')
        if flow_scope:
            gladier_scopes.append(flow_scope)
        return gladier_scopes

    @property
    def missing_authorizers(self):
        """
        :return:  a list of Globus scopes for which there are no authorizers
        """
        return [scope for scope in self.scopes if scope not in self.authorizers.keys()]

    @property
    def flows_client(self):
        """
        :return: an authorized Gloubs Automate Client
        """
        if getattr(self, '__flows_client', None) is not None:
            return self.__flows_client
        automate_authorizer = self.authorizers[
            globus_automate_client.flows_client.MANAGE_FLOWS_SCOPE
        ]
        flow_authorizer = None
        if self.gconfig.get('flow_scope'):
            flow_authorizer = self.authorizers.get(self.gconfig['flow_scope'])

        def get_flow_authorizer(*args, **kwargs):
            return flow_authorizer

        self.__flows_client = globus_automate_client.FlowsClient.new_client(
            self.client_id, get_flow_authorizer, automate_authorizer,
        )
        return self.__flows_client

    @property
    def funcx_client(self):
        """
        :return: an authorized funcx client
        """
        if getattr(self, '__funcx_client', None) is not None:
            return self.__funcx_client

        self.__funcx_client = FuncXClient()
        return self.__funcx_client

    def login(self, **login_kwargs):
        """Login to the Gladier client. This will ensure the user has the correct
        tokens configured but it DOES NOT guarantee they are in the correct group to
        run a flow. Can be run both locally and on a server.
        See help(fair_research_login.NativeClient.login) for a full list of kwargs.
        """
        nc = self.get_native_client()
        if self.is_logged_in():
            log.debug('Already logged in, skipping login.')
            return
        log.info("Initiating Native App Login...")
        log.debug(f"Requesting Scopes: {self.scopes}")
        login_kwargs["requested_scopes"] = login_kwargs.get("requested_scopes", self.scopes)
        nc.login(**login_kwargs)
        self.authorizers = nc.get_authorizers_by_scope()

    def logout(self):
        """Log out and revoke this client's tokens. This object will no longer
        be usable until a new login is called.
        """
        if not self.client_id:
            raise gladier.exc.AuthException('Gladier client must be instantiated with a '
                                            '"client_id" to use "login()!')
        log.info(f'Revoking the following scopes: {self.scopes}')
        self.get_native_client().logout()

    def is_logged_in(self):
        """
        Check if the client is logged in.

        :return: True, if there are no self.missing_authorizers. False otherwise.
        """
        return not bool(self.missing_authorizers)

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

    def get_flow_checksum(self):
        """
        Get the SHA256 checksum of the current flow definition.

        :return: sha256 hex string of flow definition
        """
        return hashlib.sha256(json.dumps(self.get_flow_definition()).encode()).hexdigest()

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

    @classmethod
    def get_funcx_function_checksum_name(cls, funcx_function):
        """
        Generate a name to refer to the checksum for a given funcx function. Based off of the
        name generated for the function self.get_funcx_function_name. Human readable, intended
        for config.

        :return:  human readable string identifier for a function checksum (for a gladier.cfg file)
        """
        return f'{cls.get_funcx_function_name(funcx_function)}_checksum'

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
                fid_name = self.get_funcx_function_name(func)
                checksum = self.get_funcx_function_checksum(func)
                checksum_name = self.get_funcx_function_checksum_name(func)
                try:
                    if not self.gconfig.get(fid_name):
                        raise gladier.exc.RegistrationException(
                            f'Tool {tool} missing funcx registration for {fid_name}')
                    if not self.gconfig.get(checksum_name):
                        raise gladier.exc.RegistrationException(
                            f'Tool {tool} with function {fid_name} '
                            f'has a function id but no checksum!')
                    if not self.gconfig[checksum_name] == checksum:
                        raise gladier.exc.FunctionObsolete(
                            f'Tool {tool} with function {fid_name} '
                            f'has changed and needs to be re-registered.')
                    funcx_ids[fid_name] = self.gconfig[fid_name]
                except (gladier.exc.RegistrationException, gladier.exc.FunctionObsolete):
                    if self.auto_registration is True:
                        log.info(f'Registering function {fid_name}')
                        self.register_funcx_function(func)
                        funcx_ids[fid_name] = self.gconfig[fid_name]
                    else:
                        raise
        return funcx_ids

    def register_funcx_function(self, function):
        """Register the functions with funcx. Ids are saved in the local gladier.cfg"""
        fxid_name = self.get_funcx_function_name(function)
        fxck_name = self.get_funcx_function_checksum_name(function)
        self.gconfig[fxid_name] = self.funcx_client.register_function(function, function.__doc__)
        self.gconfig[fxck_name] = self.get_funcx_function_checksum(function)
        self.config.save()

    def get_flow_id(self):
        """Get the current flow id for the current Gladier flow definiton.
        If self.auto_register is True, it will automatically (re)register a flow if it
        has changed on disk, otherwise raising exceptions.

        :raises: gladier.exc.FlowObsolete
        :raises: gladier.exc.NoFlowRegistered
        """
        flow_id, flow_scope = self.gconfig.get('flow_id'), self.gconfig.get('flow_scope')
        if not flow_id or not flow_scope:
            if self.auto_registration is False:
                raise gladier.exc.NoFlowRegistered(
                    f'No flow registered for {self.config_filename} under section {self.gsection}')
            flow_id = self.register_flow()
        elif self.gconfig.get('flow_checksum') != self.get_flow_checksum():
            if self.auto_registration is False:
                raise gladier.exc.FlowObsolete(
                    f'"flow_definition" on {self} has changed and needs to be re-registered.')
            self.register_flow()
            flow_id = self.gconfig['flow_id']
        return flow_id

    def register_flow(self):
        """
        Register a flow with Globus Automate. If a flow has already been registered with automate,
        the flow will attempt to update the flow instead. If not, it will deploy a new flow.

        :raises: Automate exceptions on flow deployment.
        :return: an automate flow UUID
        """
        flow_id = self.gconfig.get('flow_id')
        flow_definition = self.get_flow_definition()
        if flow_id:
            try:
                log.info(f'Flow checksum failed, updating flow {flow_id}...')
                self.flows_client.update_flow(flow_id, flow_definition)
                self.gconfig['flow_checksum'] = self.get_flow_checksum()
                self.config.save()
            except globus_sdk.exc.GlobusAPIError as gapie:
                if gapie.code == 'Not Found':
                    flow_id = None
                else:
                    raise
        if flow_id is None:
            log.info('No flow detected, deploying new flow...')
            title = f'{self.__class__.__name__} Flow'
            flow = self.flows_client.deploy_flow(flow_definition, title=title).data
            self.gconfig['flow_id'] = flow['id']
            self.gconfig['flow_scope'] = flow['globus_auth_scope']
            self.gconfig['flow_checksum'] = self.get_flow_checksum()
            self.config.save()
            flow_id = self.gconfig['flow_id']
        return flow_id

    def get_input(self):
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
            flow_input.update(tool.flow_input)
            config_values = {k: self.gconfig[k] for k in tool.flow_input.keys()
                             if k in self.gconfig}
            if config_values:
                log.info(f'{tool}: Loaded from local config {config_values}')
        return {'input': flow_input}

    def check_input(self, tool, flow_input):
        """
        Do basic checking on included input against requirements set by a tool. Raises an
        exception if the check does not 'pass'

        :param tool: The gladier.GladierBaseTool tool set in self.tools
        :param flow_input: Flow input intended to be passed to run_flow()
        :raises: gladier.exc.ConfigException
        """
        for req_input in tool.required_input:
            if req_input not in flow_input['input']:
                raise gladier.exc.ConfigException(
                    f'{tool} requires flow input value: "{req_input}"')

    def run_flow(self, flow_input=None, use_defaults=True):
        """
        Start a Globus Automate flow. Flows and Functions must be registered prior or
        self.auto_registration must be True.

        If auto-registering a flow and self.auto_login is True, this may result in two logins.
        The first is for authorizing basic tooling, and the second is to autorize the newly
        registered automate flow.

        :param flow_input: A dict of input to be passed to the automate flow. self.check_input()
                           is called on each tool to ensure basic needs are met for each.
                           Input MUST be wrapped inside an 'input' dict,
                           for example {'input': {'foo': 'bar'}}.
        :param use_defaults: Use the result of self.get_input() to populate base input for the
                             flow. All conflicting input provided by flow_input overrides
                             values set in use_defaults.
        :raise: gladier.exc.ConfigException by self.check_input()
        :raises: gladier.exc.FlowObsolete
        :raises: gladier.exc.NoFlowRegistered
        :raises: gladier.exc.RegistrationException
        :raises: gladier.exc.FunctionObsolete
        :raises: gladier.exc.AuthException
        :raises: Any globus_sdk.exc.BaseException
        """
        combine_flow_input = self.get_input() if use_defaults else dict()
        if flow_input is not None:
            if not flow_input.get('input') or len(flow_input.keys()) != 1:
                raise gladier.exc.ConfigException(
                    f'Malformed input to flow, all input must be nested under "input", got '
                    f'{flow_input.keys()}')
            combine_flow_input['input'].update(flow_input['input'])
        for tool in self.tools:
            self.check_input(tool, combine_flow_input)
        if not self.is_logged_in():
            raise gladier.exc.AuthException(f'Not Logged in, missing scopes '
                                            f'{self.missing_authorizers}')
        # When registering a flow for the first time, a special flow scope needs to be authorized
        # before the flow can begin. On first time runs, this requires an additional login.
        flow_id = self.get_flow_id()
        if not self.is_logged_in():
            log.info(f'Missing authorizers: {self.missing_authorizers}, need additional login '
                     f'to run flow.')
            if self.auto_login is True:
                self.login()
            else:
                raise gladier.exc.AuthException(
                    f'Need {self.missing_authorizers} to run flow!', self.missing_authorizers)
        flow = self.flows_client.run_flow(flow_id, self.gconfig['flow_scope'],
                                          combine_flow_input).data
        log.info(f'Started flow {self.section} flow id "{self.gconfig["flow_id"]}" with action '
                 f'"{flow["action_id"]}"')
        if flow['status'] == 'FAILED':
            raise gladier.exc.ConfigException(f'Flow Failed: {flow["details"]["description"]}')
        return flow

    def get_status(self, action_id):
        """
        Get the current status of the automate flow. Attempts to do additional work on funcx
        functions to deserialize any exception output.

        :param action_id: The globus action UUID used for this flow. The Automate flow id is
                          always the flow_id configured for this tool.
        :raises: Globus Automate exceptions from self.flows_client.flow_action_status
        :returns: a Globus Automate status object (with varying state structures)
        """
        try:
            status = self.flows_client.flow_action_status(self.get_flow_id(),
                                                          self.gconfig['flow_scope'],
                                                          action_id).data
        except KeyError:
            raise gladier.exc.ConfigException('No Flow defined, register a flow')

        try:
            return gladier.utils.automate.get_details(status)
        except (KeyError, AttributeError):
            return status

    @staticmethod
    def _default_progress_callback(response):
        if response['status'] == 'ACTIVE':
            print(f'[{response["status"]}]: {response["details"]["description"]}')

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
        callback = callback or self._default_progress_callback
        status = self.get_status(action_id)
        while status['status'] not in ['SUCCEEDED', 'FAILED']:
            status = self.get_status(action_id)
            callback(status)

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
