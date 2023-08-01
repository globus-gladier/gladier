import hashlib
import json
import logging
import warnings
from typing import Callable

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
import globus_automate_client
import globus_sdk
from gladier.managers.service_manager import ServiceManager
from globus_automate_client.flows_client import (
    MANAGE_FLOWS_SCOPE,
    RUN_FLOWS_SCOPE,
    RUN_MANAGE_SCOPE,
    RUN_STATUS_SCOPE,
    VIEW_FLOWS_SCOPE,
)

log = logging.getLogger(__name__)


def ensure_flow_registered(
    flows_manager_instance, exc: gladier.exc.RegistrationException
):
    log.info(f"Deploying/Updating flow due to: {str(exc)}")
    flows_manager_instance.register_flow()


class FlowsManager(ServiceManager):
    """
    The flows manager tracks an externally defined flow_definition and ensures it stays
    up-to-date with a deployment in the flows service. It can be run without a flow_id
    in which case it will deploy its own flow if a stored flow_id does not exist.

    The flow checksum is evaluated inside ``run_flow()``, and any updates to the flow
    will take place before the flow is started. The registration behavior can be customized
    by passing in a function for ``on_change``. Default behavior will call ``register_flow()``,
    None will disable changing the flow before starting it. The ``on_change`` signature is below:

    .. code-block::

        def on_change_callback(flows_manager_instance: FlowsManager,
                               exc: gladier.exc.RegistrationException) -> None:

    :param flow_id: Explicit flow id to use. None will result in deploying a new flow
    :param flow_definition: Flow definiton that should be used. Usually set dynamically
                            at runtime when used with a Gladier Client
    :param flow_schema: The schema to be used alongside the flow definition
    :param flow_title: The title for the Globus Flow
    :param globus_group: A Globus Group UUID. Used to grant all flow and run permissions
    :param on_change: callback on checksum mismatch or missing flow id. Default registers/deploys
                      flow, ``None`` takes no action and attempts to run "obselete" flows.
    :param redeploy_on_404: Deploy a new flow if attempting to run the current flow ID results
                            in 404. Behavior is disabled if an explicit flow_id is specified.

    When used with a Gladier Client, following items will be auto-configured and should not be
    set explicitly in the constructor:

     * flow_definition
     * flow_schema


    .. note::

        The FlowsManager class cannot be used to run flows outside of Gladier Clients due to
        internal class storage requirements. Doing so will result in an exception.
    """

    AVAILABLE_SCOPES = [
        MANAGE_FLOWS_SCOPE,
        VIEW_FLOWS_SCOPE,
        RUN_FLOWS_SCOPE,
        RUN_STATUS_SCOPE,
        RUN_MANAGE_SCOPE,
    ]

    def __init__(
        self,
        flow_id: str = None,
        flow_definition: dict = None,
        flow_schema: dict = None,
        flow_title: str = None,
        globus_group: str = None,
        on_change: Callable = ensure_flow_registered,
        redeploy_on_404: bool = True,
        **kwargs,
    ):
        self.flow_id = flow_id
        self.flow_definition = flow_definition
        self.flow_schema = flow_schema
        self.flow_title = flow_title
        self.globus_group = globus_group
        self.on_change = on_change or (lambda self, exc: None)
        self.redeploy_on_404 = redeploy_on_404

        if self.flow_id is not None:
            self.redeploy_on_404 = False
            log.info("Custom Flow ID set, redeploy_on_404 disabled.")

        super().__init__(**kwargs)

    def get_scopes(self):
        scopes = self.AVAILABLE_SCOPES.copy()
        flow_scope = self.flow_scope
        if flow_scope:
            scopes.append(flow_scope)
        return scopes

    @property
    def flow_scope(self):
        """Get the scope for a flow
        :returns: None if no flow id exists"""
        try:
            flow_id = self.get_flow_id()
        except AttributeError:
            # It's possible storage wasn't set yet, and get_flow_id() raises
            # an error here. Simply ignore it for the time being.
            flow_id = None
        if flow_id:
            # In the future, this should be gettable via
            # globus_sdk.SpecificFlowClient(flow_id).scopes.url_scope_string('flow_id'))
            scope_name = f'flow_{flow_id.replace("-", "_")}_user'
            return f"https://auth.globus.org/scopes/{flow_id}/{scope_name}"

    @property
    def flow_definition(self) -> dict:
        return self._flow_definition

    @flow_definition.setter
    def flow_definition(self, value: dict):
        self._flow_definition = value

    @property
    def flow_schema(self) -> dict:
        return self._flow_schema or {
            "input_schema": {
                "additionalProperties": True,
                "properties": {},
                "type": "object",
            }
        }

    @flow_schema.setter
    def flow_schema(self, value: dict):
        self._flow_schema = value

    @property
    def flows_client(self):
        """
        :return: an authorized Gloubs Automate Client. If a flow has been deployed,
        the client returned will be authorized to run the flow. Stale clients pre-flow-deployment
        will need to call this again in order to run flows.
        """
        if getattr(self, "_flows_client", None) is not None:
            return self._flows_client
        authorizers = self.login_manager.get_manager_authorizers()

        automate_authorizer = authorizers[
            globus_automate_client.flows_client.MANAGE_FLOWS_SCOPE
        ]
        flow_authorizer = authorizers.get(self.flow_scope)

        def get_flow_authorizer(*args, **kwargs):
            return flow_authorizer

        self._flows_client = globus_automate_client.FlowsClient.new_client(
            None,
            get_flow_authorizer,
            automate_authorizer,
        )
        return self._flows_client

    def refresh_flows_client(self) -> globus_automate_client.FlowsClient:
        self._flows_client = None
        return self.flows_client

    @staticmethod
    def get_flow_checksum(flow_definition, flow_schema):
        """
        Get the SHA256 checksum of the current flow definition.

        :return: sha256 hex string of flow definition
        """

        flow_def = json.dumps(flow_definition, sort_keys=True)
        flow_schema = json.dumps(flow_schema, sort_keys=True)
        data = (flow_def + flow_schema).encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def get_globus_urn(uuid, id_type="group"):
        """Convenience method for appending the correct Globus URN prefix on a uuid."""
        URN_PREFIXES = {
            "group": "urn:globus:groups:id:",
            "identity": "urn:globus:auth:identity:",
        }
        if id_type not in URN_PREFIXES:
            raise gladier.exc.DevelopmentException(
                '"id_type" must be one of ' f"{URN_PREFIXES.keys()}. Got: {id_type}"
            )
        return f"{URN_PREFIXES[id_type]}{uuid}"

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
            "flow_viewers",
            "flow_starters",
            "flow_administrators",
            "run_managers",
            "run_monitors",
        }
        if permission_type not in permission_types:
            raise gladier.exc.DevelopmentException(
                f"permission_type must be one of " f"{permission_types}"
            )
        return identities

    def get_flow_id(self) -> str:
        """
        Return flow id. If an ID was set on this class in the constructor, that is
        used. Otherwise, a retrieve from storage is attempted with 'flow_id' if a
        flow has been run before and a local id is cached in storage. If no flow_id
        exists from either of these locations, None is returned instead.

        :returns: flow_id uuid for deployed flow, or None if it does not exist
        """
        return self.flow_id or self.storage.get_value("flow_id")

    def flow_changed(self) -> bool:
        """
        Returns True if a flow id exists and the stored checksum matches the set
        flow_definition. False otherwise.
        :raises: Nothing
        """
        try:
            self.check_flow()
        except gladier.exc.RegistrationException:
            return True
        return False

    def check_flow(self):
        """
        Check if the flow has changed by validating the current flow_definition against
        the stored checksum. Raises an exception if the checksums do not match.

        :raises: gladier.exc.NoFlowRegistered if no flow has been registered
        :raises: gladier.exc.FlowObsolete if the stored flow checksums do not match
        """
        flow_id = self.get_flow_id()
        flow_checksum = self.storage.get_value("flow_checksum")
        if not flow_id:
            message = "No flow_id set on flow manager and no id tracked in storage."
            log.info(message)
            raise gladier.exc.NoFlowRegistered(message)
        elif flow_checksum != self.get_flow_checksum(
            self.flow_definition, self.flow_schema
        ):
            message = f'"flow_definition" on {self} has changed and needs to be re-registered.'
            log.info(message)
            raise gladier.exc.FlowObsolete(message)

    def sync_flow(self) -> str:
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
            self.check_flow()
        except gladier.exc.RegistrationException as exc:
            self.on_change(self, exc)
        return self.get_flow_id()

    def register_flow(self) -> str:
        """
        Deploy the current flow_definition. If a flow_id exists, the flow is updated
        instead. If the flow does not exist (404) and redeploy_on_404 is set, the flow will
        be automatically re-deployed with a new flow id.



        Note: If a new flow is deployed, or an existing scope adds unique Action Providers,
        a new login will be needed before the flow can be run.
        :raises: globus_sdk.exc.GlobusAPIError on error deploying flow
        :return: an automate flow UUID
        """
        flow_id = self.get_flow_id()
        flow_permissions = {
            p_type: self.get_flow_permission(p_type)
            for p_type in ["flow_viewers", "flow_starters", "flow_administrators"]
            if self.get_flow_permission(p_type)
        }
        log.debug(f'Flow permissions set to: {flow_permissions or "Flows defaults"}')
        flow_kwargs = flow_permissions
        # Input schema is a required field and must be part of all flows.
        flow_kwargs["input_schema"] = self.flow_schema
        if flow_id:
            try:
                log.info(f"Flow checksum failed, updating flow {flow_id}...")
                self.flows_client.update_flow(
                    flow_id, self.flow_definition, **flow_kwargs
                )
                self.storage.set_value(
                    "flow_checksum",
                    self.get_flow_checksum(self.flow_definition, self.flow_schema),
                )
            except globus_sdk.exc.GlobusAPIError as gapie:
                if gapie.http_status == 404 and self.redeploy_on_404:
                    flow_id = None
                else:
                    raise
        if flow_id is None:
            log.info("No flow detected, deploying new flow...")
            flow = self.flows_client.deploy_flow(
                self.flow_definition, title=self.flow_title, **flow_kwargs
            ).data
            log.debug(f'Flow deployed with id {flow["id"]}')
            self.storage.set_value("flow_id", flow["id"])
            self.storage.set_value(
                "flow_checksum",
                self.get_flow_checksum(self.flow_definition, self.flow_schema),
            )
            self.login_manager.add_requirements([flow["globus_auth_scope"]])
            self.refresh_flows_client()

        return flow_id

    def purge_flow(self):
        """
        Remove the stored flow_id and flow_checksum.
        """
        self.storage.del_value("flow_id")
        self.storage.del_value("flow_checksum")

    def run_flow(self, **kwargs):
        flow_id = self.get_flow_id()

        permissions = {
            p_type: self.get_flow_permission(p_type)
            for p_type in ["run_managers", "run_monitors"]
            if self.get_flow_permission(p_type)
        }
        log.debug(f'Flow run permissions set to: {permissions or "Flows defaults"}')
        kwargs.update(permissions)

        # Ensure the label is not longer than 64 chars
        if "label" in kwargs:
            label = kwargs["label"]
            kwargs["label"] = (label[:62] + "..") if len(label) > 64 else label

        try:
            flow = self.flows_client.run_flow(flow_id, self.flow_scope, **kwargs).data
        except globus_sdk.exc.GlobusAPIError as gapie:
            if gapie.http_status == 404 and self.redeploy_on_404:
                log.warning(
                    f"Flow {flow_id} returned 404 and is either deleted or unavailable. "
                    f"Purging flow_id from config file..."
                )
                # On a 404, Gladier can't do anything since it cannot access the old flow.
                # Therefore, purge the old flow and deploy a new one.
                self.purge_flow()
                # Ensure the new flow is deployed
                self.sync_flow()
                # Fetch the new flow id
                flow_id = self.get_flow_id()
                flow = self.flows_client.run_flow(
                    flow_id, self.flow_scope, **kwargs
                ).data
            elif gapie.http_status == 400:
                # Typically, 400s with strange text error messages are due to dependent scopes
                # changing on the flow between runs, eg add a new Transfer AP and now it needs
                # a tranfer scope, which the previous access token didn't have. Attempt to pick
                # the dependent scope problem out of any generic 400, or re-raise if not.
                try:
                    log.debug("Encountered error when running flow", exc_info=True)
                    automate_error_message = json.loads(gapie.text)
                    detail_message = automate_error_message["error"]["detail"]
                    if "unable to get tokens for scopes" in detail_message:
                        self.login_manager.add_scope_change([self.flow_scope])
                        self.refresh_flows_client()
                        log.info("Initiating new login for dependent scope change")
                        flow = self.flows_client.run_flow(
                            flow_id, self.flow_scope, **kwargs
                        ).data
                    else:
                        raise
                except (TypeError, ValueError):
                    raise gapie from None
            else:
                raise
        log.info(
            f'Started flow {kwargs.get("label")} flow id '
            f'"{flow_id}" with run "{flow["run_id"]}"'
        )

        if flow["status"] == "FAILED":
            raise gladier.exc.ConfigException(
                f'Flow Failed: {flow["details"]["description"]}'
            )
        return flow

    def get_status(self, run_id):
        """
        Get the current status of the automate flow. Attempts to do additional work on compute
        functions to deserialize any exception output.

        :param run_id: The globus action UUID used for this flow. The Automate flow id is
                          always the flow_id configured for this tool.
        :raises: Globus Automate exceptions from self.flows_client.flow_action_status
        :returns: a Globus Automate status object (with varying state structures)
        """
        status = self.flows_client.flow_action_status(
            self.get_flow_id(), self.flow_scope, run_id
        ).data
        try:
            return gladier.utils.automate.get_details(status)
        except (KeyError, AttributeError):
            return status

    @staticmethod
    def _default_progress_callback(response):
        if response["status"] == "ACTIVE":
            print(f'[{response["status"]}]: {response["details"]["description"]}')

    def progress(self, run_id, callback=None):
        """
        Continuously call self.get_status() until the flow completes. Each status response is
        used as a parameter to the provided callback, by default will use the builtin callback
        to print the current state to stdout.

        :param run_id: The action id for a running flow. The flow is automatically pulled
                          based on the current tool's flow_definition.
        :param callback: The function to call with the result from self.get_status. Must take
                         a single parameter: mycallback(self.get_status())
        """
        callback = callback or self._default_progress_callback
        status = self.get_status(run_id)
        while status["status"] not in ["SUCCEEDED", "FAILED"]:
            status = self.get_status(run_id)
            callback(status)

    def get_details(self, run_id, state_name):
        """
        Attempt to extrapolate details from get_status() for a given state_name define in the flow
        definition. Note: This is usually only possible when a flow completes.

        :param run_id: The run_id for this flow. Flow id is automatically determined based
                          on the current tool being run.
        :param state_name: The state in the automate definition to fetch
        :returns: sub-dict of get_status() describing the :state_name:.
        """
        return gladier.utils.automate.get_details(self.get_status(run_id), state_name)
