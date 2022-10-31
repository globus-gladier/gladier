import logging
import hashlib
import json
from typing import Callable

import globus_sdk
import globus_automate_client

import gladier
from gladier.managers.service_manager import ServiceManager
import gladier.storage.config
import gladier.utils.dynamic_imports
import gladier.utils.automate
import gladier.utils.name_generation
import gladier.storage.migrations
import gladier.utils.tool_alias
import gladier.utils.funcx_login_manager
import gladier.exc
import gladier.version

from gladier.exc import GladierException

from globus_automate_client.flows_client import (
    MANAGE_FLOWS_SCOPE,
    VIEW_FLOWS_SCOPE,
    RUN_FLOWS_SCOPE,
    RUN_STATUS_SCOPE,
    RUN_MANAGE_SCOPE,
)

log = logging.getLogger(__name__)


def on_change_callback(flows_manager_instance, exc: gladier.exc.RegistrationException,
                       flow_definition: dict):
    log.info(f'Deploying/Updating flow due to: {str(exc)}')
    flows_manager_instance.register_flow(flow_definition)


class FlowsManager(ServiceManager):

    AVAILABLE_SCOPES = [
        MANAGE_FLOWS_SCOPE,
        VIEW_FLOWS_SCOPE,
        RUN_FLOWS_SCOPE,
        RUN_STATUS_SCOPE,
        RUN_MANAGE_SCOPE,
    ]

    def __init__(self,
                 globus_group: str = None,
                 subscription_id: str = None,
                 flow_id: str = None,
                 on_change: Callable = on_change_callback,
                 **kwargs):
        super().__init__(**kwargs)
        self.globus_group = globus_group
        self.subscription_id = subscription_id
        self.on_change = on_change
        self._flow_definition = None
        self._flow_schema = None

        if flow_id is not None:
            self.storage.set_value('flow_id', flow_id)

    def get_scopes(self):
        scopes = self.AVAILABLE_SCOPES.copy()
        flow_scope = self.storage.get_value('flow_scope')
        if flow_scope:
            scopes.append(flow_scope)
        return scopes

    @property
    def flow_scope(self):
        flow_id = self.storage.get_value('flow_id')
        dummy_cli = globus_automate_client.FlowsClient.new_client(None, None)
        return dummy_cli.scope_for_flow(flow_id)

    @property
    def flow_definition(self) -> dict:
        if self._flow_definition is None:
            raise GladierException('No Flow definition provided to flows manager.')
        return self._flow_definition

    @flow_definition.setter
    def flow_definition(self, value: dict):
        self._flow_definition = value

    @property
    def flow_schema(self) -> dict:
        return self._flow_schema or {
            'input_schema': {
                'additionalProperties': True,
                'properties': {},
                'type': 'object'
            }
        }

    @flow_schema.setter
    def flow_schema(self, value: dict):
        self._flow_scema = value

    @property
    def flows_client(self):
        """
        :return: an authorized Gloubs Automate Client
        """
        if getattr(self, '_flows_client', None) is not None:
            return self._flows_client
        authorizers = self.login_manager.get_manager_authorizers()

        automate_authorizer = authorizers[
            globus_automate_client.flows_client.MANAGE_FLOWS_SCOPE
        ]
        flow_authorizer = authorizers.get(self.flow_scope)

        def get_flow_authorizer(*args, **kwargs):
            return flow_authorizer

        self._flows_client = globus_automate_client.FlowsClient.new_client(
            None, get_flow_authorizer, automate_authorizer,
        )
        return self._flows_client

    def refresh_flows_client(self) -> globus_automate_client.FlowsClient:
        self._flows_client = None
        return self.flows_client

    @staticmethod
    def get_flow_checksum(flow_definition):
        """
        Get the SHA256 checksum of the current flow definition.

        :return: sha256 hex string of flow definition
        """
        return hashlib.sha256(json.dumps(flow_definition, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def get_globus_urn(uuid, id_type='group'):
        """Convenience method for appending the correct Globus URN prefix on a uuid."""
        URN_PREFIXES = {
            'group': 'urn:globus:groups:id:',
            'identity': 'urn:globus:auth:identity:'
        }
        if id_type not in URN_PREFIXES:
            raise gladier.exc.DevelopmentException('"id_type" must be one of '
                                                   f'{URN_PREFIXES.keys()}. Got: {id_type}')
        return f'{URN_PREFIXES[id_type]}{uuid}'

    def get_flow_permission(self, permission_type, identities=None):
        """
        This function is a generic shim that should work for most Gladier clients that
        want basic permissions that will work with a single Globus Group. This method can be
        overridden to change any of the automate defaults:

        permission_type for deploying flows:
            'flow_viewers', 'flow_starters', 'flow_administrators',

        permission_type for running flows:
            'run_managers', 'run_monitors'

        By default, always returns either None for using automate defaults, or setting every
        permission_type above to use the set client `globus_group`.
        """
        if identities is None and self.globus_group:
            identities = [self.get_globus_urn(self.globus_group)]
        permission_types = {
            'flow_viewers', 'flow_starters', 'flow_administrators', 'run_managers', 'run_monitors'
        }
        if permission_type not in permission_types:
            raise gladier.exc.DevelopmentException(f'permission_type must be one of '
                                                   f'{permission_types}')
        return identities

    def get_flow_id(self):
        return self.storage.get_value('flow_id')

    def has_changed(self, flow_definition: dict):
        try:
            self.check_flow(flow_definition)
        except gladier.exc.RegistrationException:
            return True
        return False

    def check_flow(self, flow_definition: dict):
        flow_id = self.get_flow_id()
        flow_checksum = self.storage.get_value('flow_checksum')
        if not flow_id:
            raise gladier.exc.NoFlowRegistered(
                'No flow_id set on flow manager and no id tracked in storage.')
        elif flow_checksum != self.get_flow_checksum(flow_definition):
            raise gladier.exc.FlowObsolete(
                f'"flow_definition" on {self} has changed and needs to be re-registered.')

    def validate_flow(self, flow_definition: dict) -> str:
        """
        Get the current flow id for the current Gladier flow definition.
        If self.auto_register is True, it will automatically (re)register a flow if it
        has changed on disk, otherwise raising exceptions.

        :param flow_definition: A complete deployable Flow Definition. Will replace existing
        flow definition if it differs.

        :raises: gladier.exc.FlowObsolete
        :raises: gladier.exc.NoFlowRegistered
        """
        try:
            self.check_flow(flow_definition)
        except gladier.exc.RegistrationException as exc:
            self.on_change(self, exc, flow_definition)
        return self.storage.get_value('flow_id')

    def register_flow(self, flow_definition):
        """
        Register a flow with Globus Automate. If a flow has already been registered with automate,
        the flow will attempt to update the flow instead. If not, it will deploy a new flow.

        :raises: Automate exceptions on flow deployment.
        :return: an automate flow UUID
        """
        self.flow_definition = flow_definition
        flow_id = self.get_flow_id()
        flow_permissions = {
            p_type: self.get_flow_permission(p_type)
            for p_type in ['flow_viewers', 'flow_starters', 'flow_administrators']
            if self.get_flow_permission(p_type)
        }
        log.debug(f'Flow permissions set to: {flow_permissions or "Flows defaults"}')
        flow_kwargs = flow_permissions
        # Input schema is a required field and must be part of all flows.
        flow_kwargs['input_schema'] = self.flow_schema
        if self.subscription_id:
            flow_kwargs['subscription_id'] = self.subscription_id
        if flow_id:
            try:
                log.info(f'Flow checksum failed, updating flow {flow_id}...')
                self.flows_client.update_flow(flow_id, self.flow_definition, **flow_kwargs)
                self.storage.set_value('flow_checksum',
                                       self.get_flow_checksum(self.flow_definition))
            except globus_sdk.exc.GlobusAPIError as gapie:
                if gapie.code == 'Not Found':
                    flow_id = None
                else:
                    raise
        if flow_id is None:
            log.info('No flow detected, deploying new flow...')
            title = f'{self.__class__.__name__} Flow'

            flow = self.flows_client.deploy_flow(self.flow_definition, title=title,
                                                 **flow_kwargs).data
            self.storage.set_value('flow_id', flow['id'])
            self.storage.set_value('flow_checksum', self.get_flow_checksum(self.flow_definition))
            self.login_manager.add_requirements([flow['globus_auth_scope']])
            self.refresh_flows_client()

        return flow_id

    def run_flow(self, **kwargs):
        r"""
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
        flow_id = self.get_flow_id()

        permissions = {
            p_type: self.get_flow_permission(p_type)
            for p_type in ['run_managers', 'run_monitors']
            if self.get_flow_permission(p_type)
        }
        log.debug(f'Flow run permissions set to: {permissions or "Flows defaults"}')
        kwargs.update(permissions)

        # Ensure the label is not longer than 64 chars
        if 'label' in kwargs:
            label = kwargs['label']
            kwargs['label'] = (label[:62] + '..') if len(label) > 64 else label

        try:
            flow = self.flows_client.run_flow(flow_id, self.flow_scope, **kwargs).data
        except globus_sdk.exc.GlobusAPIError as gapie:
            log.debug('Encountered error when running flow', exc_info=True)
            automate_error_message = json.loads(gapie.message)
            detail_message = automate_error_message['error']['detail']
            if 'unable to get tokens for scopes' in detail_message:
                self.login_manager.add_scope_change([self.flow_scope])
                self.refresh_flows_client()
                log.info('Initiating new login for dependent scope change')
                flow = self.flows_client.run_flow(flow_id, self.flow_scope, **kwargs).data
            elif gapie.http_status == 404:
                log.warning(f'Flow {flow_id} returned 404 and is either deleted or unavailable. '
                            f'Purging flow_id from config file...')
                # On a 404, Gladier can't do anything since it cannot access the old flow.
                # Therefore, purge the old flow and deploy a new one by calling get_flow_id()
                cfg = self.get_cfg()
                del cfg[self.section]['flow_id']
                cfg.save()
                # Ensure the new flow is deployed
                self.validate_flow(self.flow_definition)
                # Ensure the new flow scope is added to login so it can be run
                self.refresh_flows_client()
                # Run the flow
                flow = self.flows_client.run_flow(flow_id, self.flow_scope, **kwargs).data
            else:
                raise
        log.info(f'Started flow {kwargs.get("label")} flow id '
                 f'"{flow_id}" with run "{flow["run_id"]}"')

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
            status = self.flows_client.flow_action_status(
                self.get_flow_id(), self.storage.get_value('flow_scope'), action_id
            ).data
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
