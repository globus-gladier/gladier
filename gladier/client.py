from __future__ import annotations

import typing as t

import logging
import os
import pathlib
from collections.abc import Iterable

import gladier
import gladier.exc
import gladier.managers.compute_login_manager
import gladier.storage.config
import gladier.storage.migrations
import gladier.utils.automate
import gladier.utils.dynamic_imports
import gladier.utils.name_generation
import gladier.utils.tool_alias
import gladier.version
from gladier.base import GladierBaseTool
from gladier.managers import ComputeManager, FlowsManager
from gladier.managers.login_manager import (
    AutoLoginManager,
    BaseLoginManager,
    ConfidentialClientLoginManager,
)
from gladier.storage.tokens import GladierSecretsConfig

log = logging.getLogger(__name__)


class GladierBaseClient(object):
    """
    The Gladier Client ties together commonly used compute functions
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
         @generate_flow_definition. Changes are tracked on each run, and will result
         in a flow re-deploy on any change.
    * flow_schema (default: {})
       * A flow schema to accompany the flow definition. Schema is checked on each
         run and are re-deployed if it changes. Overrides any existing schema set
         on a given flow_manager instance unless unset.
    * subscription_id (default: None)
       * A subscription ID to associate with a flow. This typically is automatically
         determined and does not need to be supplied, but may be required if the user
         has more than one subscription
    * secret_config_filename (default: ``~/.gladier-secrets.cfg``)
       * Storage are for Globus Tokens and general storage
    * app_name (default: 'Gladier Client')
       * The app name used during a login flow
    * client_id
       * The Globus Client ID used for native logins
    * globus_group (default: None)
       * A Globus Group to be applied to all flow/run permissions. Group will automatically be
         added to flow_viewers, flow_starters, flow_administrators, run_managers, run_monitors
    * alias_class (default: gladier.utils.tool_alias.StateSuffixVariablePrefix)
       * The default class used to for applying aliases to Tools

    The following Environment variables can be set and are recognized by Gladier Clients:

    * GLADIER_CLIENT_ID -- Used only for setting confidential client credentials instead of user
        credentials. This is a convenience feature, as an alternative to using a
        custom login_manager
    * GLADIER_CLIENT_SECRET -- Secret used for confidential clients, using with GLADIER_CLIENT_ID

    Default options are intended for CLI usage and maximum user convenience.

    :param auto_registration: Automatically register functions or flows if they are not
                              previously registered or obsolete.
    :param login_manager: Class defining login behavior. Defaults to AutoLoginManager, and
                          will auto-login when additional scopes are needed.
    :param flows_manager: A flows manager class with customized behavior. Attrs like group
                          and login_manager will automatically be set if None
    :param compute_manager: A compute manager class with customized behavior. EXPERIMENTAL.
                            Will likely change in the future!
    :raises gladier.exc.AuthException: if authorizers given are insufficient

    """

    secret_config_filename: t.Optional[str] = None
    app_name: t.Optional[str] = "Gladier Client"
    client_id: str = "f1631610-d9e4-4db2-81ba-7f93ad4414e3"
    subscription_id: t.Optional[str] = None
    globus_group: t.Optional[str] = None
    alias_class = gladier.utils.tool_alias.StateSuffixVariablePrefix

    def __init__(
        self,
        auto_registration: bool = True,
        login_manager: t.Optional[BaseLoginManager] = None,
        flows_manager: t.Optional[FlowsManager] = None,
        compute_manager: t.Optional[ComputeManager] = None,
    ):
        self._tools = None
        self.storage = self._determine_storage()
        self.login_manager = login_manager or self._determine_login_manager(
            self.storage
        )

        self.flows_manager = flows_manager or FlowsManager(
            auto_registration=auto_registration, subscription_id=self.subscription_id
        )
        if self.globus_group:
            self.flows_manager.globus_group = self.globus_group
        if not self.flows_manager.flow_title:
            self.flows_manager.flow_title = f"{self.__class__.__name__} flow"

        self.compute_manager = compute_manager or ComputeManager(
            auto_registration=auto_registration
        )
        self.storage.update()

        for man in (self.flows_manager, self.compute_manager):
            man.set_storage(self.storage, replace=False)
            man.set_login_manager(self.login_manager, replace=False)
            man.register_scopes()

    def _get_confidential_client_credentials(self):
        return os.getenv("GLADIER_CLIENT_ID"), os.getenv("GLADIER_CLIENT_SECRET")

    def _determine_storage(self):
        """
        Determine the storage location for Gladier. This is typically in the ~/.gladier directory,
        but can be changed by setting the ``secret_config_filename`` on the class.

        Setting GLADIER_CLIENT_ID will change the filename to the client id, so that config
        items will not conflict with user details.
        """
        # Storage will automatically change if client credentials are detected.
        CLI_ID, _ = self._get_confidential_client_credentials()
        client_id = CLI_ID or self.client_id

        if self.secret_config_filename:
            storage_filename = pathlib.Path(self.secret_config_filename)
        else:
            storage_filename = pathlib.Path(f"~/.gladier/{client_id}.cfg").expanduser()
            storage_filename.parent.mkdir(exist_ok=True)

        storage_section = gladier.utils.name_generation.get_snake_case(
            self.__class__.__name__
        )
        storage_tokens_section = f"tokens_{client_id}"

        return GladierSecretsConfig(
            storage_filename, storage_section, tokens_section=storage_tokens_section
        )

    def _determine_login_manager(self, storage):
        """
        Determine the login manager to use for Glaider. First searches for evnironment
        variables for a confidential client, then defaults to an AutoLoginManager using
        a native client id set as ``client_id`` on this class.
        """
        CLI_ID, CLI_SEC = self._get_confidential_client_credentials()
        if CLI_ID and CLI_SEC:
            log.info(
                "Client Credentials detected, using custom internal storage for "
                "storing tokens."
            )
            return ConfidentialClientLoginManager(CLI_ID, CLI_SEC, storage=storage)
        else:
            return AutoLoginManager(self.client_id, storage, self.app_name)

    @staticmethod
    def get_gladier_defaults_cls(tool_ref, alias_class=None):
        """
        Load a Gladier default class (gladier.GladierBaseTool) by import string. For
        Example: get_gladier_defaults_cls('gladier.tools.hello_world.HelloWorld')

        :param tool_ref: A tool ref can be a dotted import string or an actual GladierBaseTool
                         class.
        :return: gladier.GladierBaseTool
        """
        log.debug(f"Looking for Gladier tool: {tool_ref} ({type(tool_ref)})")
        if isinstance(tool_ref, str):
            default_cls = gladier.utils.dynamic_imports.import_string(tool_ref)
            _, alias = gladier.utils.dynamic_imports.parse_alias(tool_ref)
            default_inst = default_cls(alias, alias_class)
            if issubclass(type(default_inst), gladier.base.GladierBaseTool):
                return default_inst
            raise gladier.exc.ConfigException(
                f"{default_inst} is not of type " f"{gladier.base.GladierBaseTool}"
            )
        elif isinstance(tool_ref, (gladier.base.GladierBaseTool, gladier.BaseState)):
            return tool_ref
        else:
            cls_inst = tool_ref()
            if isinstance(cls_inst, gladier.base.GladierBaseTool):
                return cls_inst
            raise gladier.exc.ConfigException(
                f'"{tool_ref}" must be a {gladier.base.GladierBaseTool} or a dotted import '
                "string "
            )

    @property
    def version(self):
        return gladier.version.__version__

    @property
    def tools(self):
        """
        Load the current list of tools configured on this class

        :return: a list of subclassed instances of gladier.GladierBaseTool
        """
        if getattr(self, "_tools", None):
            return self._tools

        gtools = getattr(self, "gladier_tools", [])
        if not gtools or not isinstance(gtools, Iterable):
            if not self.get_flow_definition():
                raise gladier.exc.ConfigException(
                    '"gladier_tools" must be a defined list of Gladier Tools. '
                    'Ex: ["gladier.tools.hello_world.HelloWorld"]'
                )
        self._tools = [
            self.get_gladier_defaults_cls(gt, self.alias_class) for gt in gtools
        ]
        return self._tools

    @property
    def scopes(self):
        """
        The current list of scopes required by this class. This changes if there
        is a flow configured in the local Gladier config file, otherwise it will
        only consist of basic scopes for running the compute client/flows client/etc

        :return: list of globus scopes required by this client
        """
        return list(self.login_manager.get_authorizers().keys())

    @property
    def missing_authorizers(self):
        """
        :return:  a list of Globus scopes for which there are no authorizers
        """
        return self.login_manager.missing_authorizers

    def login(self):
        """
        Call ``login()`` on the configured login manager. Attepmts to prepare the user to run flows,
        but may require being called twice if a flow is not yet deployed. Automatically called
        internally by ``run_flow()`` if required.
        """
        if self.login_manager.missing_authorizers:
            self.login_manager.login(self.login_manager.missing_authorizers)

    def logout(self):
        """Call ``logout()`` on the login manager, to revoke saved tokens and deactivate the
        current flow. The flow_id and function ids/checksums are unaffected, and can be re-used
        after another invocation of ``login()``.
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
        try:
            if isinstance(self.flow_definition, dict):
                return self.flow_definition
            elif isinstance(self.flow_definition, str):
                return self.get_gladier_defaults_cls(
                    self.flow_definition
                ).flow_definition
            else:
                raise gladier.exc.ConfigException(
                    '"flow_definition" must be a dict or an import string '
                    "to a sub-class of type "
                    '"gladier.GladierBaseTool"'
                )
        except AttributeError:
            raise gladier.exc.ConfigException(
                '"flow_definition" was not set on ' f"{self.__class__.__name__}"
            )

    def get_flow_schema(self):
        """
        Get the flow schema attached to this class.
        """
        return getattr(self, "flow_schema", None)

    def sync_flow(self):
        self.flows_manager.flow_definition = self.get_flow_definition()
        schema = self.get_flow_schema()
        if schema:
            self.flows_manager.flow_schema = schema
        self.flows_manager.sync_flow()

    def run_flow(self, flow_input=None, use_defaults=True, **flow_kwargs):
        r"""
        Start a Globus Automate flow. By default, the flow definiton is checked and synced if it
        has changed locally or deployed if it does not exist.

        If a group is set, run permissions are updated and applied to the run (includes
        'run_managers', 'run_monitors').

        Any scope changes required post-deployment/update are propogated through the login_manager
        and may require an additional login. A new flow checksum/id may be tracked in storage if
        the flow changed or was newly deployed.

        The run_flow method shadows the globus-automate-client method for running flows documented
        here: https://globus-automate-client.readthedocs.io/en/latest/python_sdk_reference.html#globus_automate_client.flows_client.FlowsClient.run_flow  # noqa
        Additional arguments matching the method signature may be added. Common ones include the
        following:

        * **label** (Optional[str]) An optional label which can be used to identify this run
        * **tags** (Optional[List[str]]) Tags that will be associated with this Run.

        Example:

        .. code-block:: python

            myinput = {
                "input": {
                    "args": "cat /proc/version",
                    "capture_output": True,
                    "compute_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
                }
            }
            my_client.run_flow(myinput, label='Check Version', tags=['version', 'POSIX'])

        :param flow_input: A dict of input to be passed to the automate flow. self.check_input()
                           is called on each tool to ensure basic needs are met for each.
                           Input MUST be wrapped inside an 'input' dict,
                           for example {'input': {'foo': 'bar'}}.

        :param use_defaults: Use the result of self.get_input() to populate base input for the
                             flow. All conflicting input provided by flow_input overrides
                             values set in use_defaults.
        :param \**flow_kwargs: Set several keyed arguments that include the label to be used
                               in the automate app. If no label is passed the standard automate
                               label is used. Also ensure label <= 64 chars long.
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
            if not flow_input.get("input") or len(flow_input.keys()) != 1:
                raise gladier.exc.ConfigException(
                    f'Malformed input to flow, all input must be nested under "input", got '
                    f"{flow_input.keys()}"
                )
            combine_flow_input["input"].update(flow_input["input"])
        for tool in self.tools:
            self.check_input(tool, combine_flow_input)

        self.sync_flow()
        return self.flows_manager.run_flow(body=combine_flow_input, **flow_kwargs)

    def get_compute_function_ids(self):
        """Get all compute function ids for this run, registering them if there are no ids
        stored in the local Gladier config file OR the stored function id checksums do
        not match the actual functions provided on each of the Gladier tools. If register
        is False, no changes to the config will be made and exceptions will be raised instead.

        :raises: gladier.exc.RegistrationException
        :raises: gladier.exc.FunctionObsolete
        :returns: a dict of function ids where keys are names and values are compute function ids.
        """
        compute_ids = dict()
        for tool in self.tools:
            log.debug(f"Checking functions for {tool}")
            compute_funcs = getattr(tool, "compute_functions", []) + getattr(
                tool, "funcx_functions", []
            )
            if not compute_funcs:
                log.warning(f"Tool {tool} did not define any compute functions!")
            if not compute_funcs and not isinstance(compute_funcs, Iterable):
                raise gladier.exc.DeveloperException(
                    f'Attribute "compute_functions" on {tool} needs to be an iterable! Found '
                    f"{type(compute_funcs)}"
                )

            for func in compute_funcs:
                name, val = self.compute_manager.validate_function(tool, func)
                compute_ids[name] = val
        return compute_ids

    def get_flow_id(self) -> t.Optional[str]:
        """
        Get the flow id from the :ref:`sdk_reference_flows_manager`.
        """
        return self.flows_manager.get_flow_id()

    def get_input(self) -> dict:
        """
        Get compute function ids, compute endpoints, and each tool's default input. Default
        input may not be enough to run the flow. For example if a tool does processing on a
        local filesystem, the file will always need to be provided by the user when calling
        run_flow().

        Defaults rely on GladierBaseTool.flow_input defined separately for each tool.

        :return: input for a flow wrapped in an 'input' dict. For example:
                 {'input': {'foo': 'bar'}}
        """
        flow_input = self.get_compute_function_ids()
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
            log.debug(
                f"{tool}: Looking for overrides for the following input keys: {input_keys}"
            )
            override_values = {
                k: self.storage.get_value(k)
                for k in input_keys
                if self.storage.get_value(k) is not None
            }
            if override_values:
                log.info(
                    f"Updates from {self.storage.filename}: {list(override_values.keys())}"
                )
                flow_input.update(override_values)
        return {"input": flow_input}

    def check_input(self, tool: GladierBaseTool, flow_input: dict):
        """
        Do basic checking on included input against requirements set by a tool. Raises an
        exception if the check does not 'pass'

        :param tool: The gladier.GladierBaseTool tool set in self.tools
        :param flow_input: Flow input intended to be passed to run_flow()
        :raises: gladier.exc.ConfigException
        """
        for req_input in tool.get_required_input():
            if req_input not in flow_input["input"]:
                raise gladier.exc.ConfigException(
                    f'{tool} requires flow input value: "{req_input}"'
                )

    def get_status(self, action_id: str):
        """
        Get the current status of the automate flow. Attempts to do additional work on compute
        functions to deserialize any exception output.

        :param action_id: The globus action UUID used for this flow. The Automate flow id is
                          always the flow_id configured for this tool.
        :raises: Globus Automate exceptions from self.flows_client.flow_action_status
        :returns: a Globus Automate status object (with varying state structures)
        """
        return self.flows_manager.get_status(action_id)

    def progress(self, action_id, callback=None, delay=2):
        """
        Continuously call self.get_status() until the flow completes. Each status response is
        used as a parameter to the provided callback, by default will use the builtin callback
        to print the current state to stdout.

        :param action_id: The action id for a running flow. The flow is automatically pulled
                          based on the current tool's flow_definition.
        :param callback: The function to call with the result from self.get_status. Must take
                         a single parameter: mycallback(self.get_status())
        """
        return self.flows_manager.progress(action_id, callback=callback, delay=delay)

    def get_details(self, action_id, state_name):
        """
        Attempt to extrapolate details from get_status() for a given state_name define in the flow
        definition. Note: This is usually only possible when a flow completes.

        :param action_id: The action_id for this flow. Flow id is automatically determined based
                          on the current tool being run.
        :param state_name: The state in the automate definition to fetch
        :returns: sub-dict of get_status() describing the :state_name:.
        """
        return gladier.utils.automate.get_details(
            self.get_status(action_id), state_name
        )


class GladierClient(GladierBaseClient):
    def __init__(
        self,
        flow_definition: t.Mapping[str, t.Any],
        auto_registration: bool = True,
        login_manager: t.Optional[BaseLoginManager] = None,
        flows_manager: t.Optional[FlowsManager] = None,
    ):
        super().__init__(
            auto_registration=auto_registration,
            login_manager=login_manager,
            flows_manager=flows_manager,
        )
        self.flow_definition = flow_definition
