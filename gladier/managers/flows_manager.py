import hashlib
import json
import time
import logging
import copy
import warnings
import typing as t

import globus_sdk
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
import globus_sdk
from gladier.managers.service_manager import ServiceManager

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
    :param subscription_id: A subscription ID to associate with a flow. This typically is automatically
                            determined and does not need to be supplied, but may be required if the user
                            has more than one subscription
    :param globus_group: A Globus Group UUID. Used to grant all flow and run permissions
    :param on_change: callback on checksum mismatch or missing flow id. Default registers/deploys
                      flow, ``None`` takes no action and attempts to run "obselete" flows.
    :param redeploy_on_404: Deploy a new flow if attempting to run the current flow ID results
                            in 404. Behavior is disabled if an explicit flow_id is specified.
    :param flow_kwargs: Any additional arguments passed to ``flows_client.create_flow`` or
        ``flows_client.update_flow``. Supersedes any Gladier defaults, and will raise a warning
        if any exist. For example, passing ``globus_group`` to this class and ``flow_administrators``
        as a ``flow_kwargs`` will only result in the ``flows_kwargs`` arguments taking effect.
    :param run_kwargs: Deploy a new flow if attempting to run the current flow ID results
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
        globus_sdk.FlowsClient.scopes.manage_flows,
        globus_sdk.FlowsClient.scopes.view_flows,
        globus_sdk.FlowsClient.scopes.run,
        globus_sdk.FlowsClient.scopes.run_status,
        globus_sdk.FlowsClient.scopes.run_manage,
    ]

    def __init__(
        self,
        flow_id: t.Optional[str] = None,
        flow_definition: t.Optional[dict] = None,
        flow_schema: t.Optional[dict] = None,
        flow_title: t.Optional[str] = None,
        subscription_id: t.Optional[str] = None,
        globus_group: t.Optional[str] = None,
        on_change: t.Optional[t.Callable] = ensure_flow_registered,
        redeploy_on_404: bool = True,
        flow_kwargs: dict = None,
        run_kwargs: dict = None,
        **kwargs,
    ):
        self.flow_id = flow_id
        self.flow_definition = flow_definition
        self.flow_schema = flow_schema
        self.flow_title = flow_title
        self.subscription_id = subscription_id
        self.globus_group = globus_group
        self.on_change = on_change or (lambda self, exc: None)
        self.redeploy_on_404 = redeploy_on_404

        self.flow_kwargs = flow_kwargs or dict()
        self.run_kwargs = run_kwargs or dict()

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
        return self._flow_schema or {"additionalProperties": True}

    @flow_schema.setter
    def flow_schema(self, value: dict):
        self._flow_schema = value

    @property
    def flows_client(self) -> globus_sdk.FlowsClient:
        """
        :return: an authorized Gloubs Automate Client. If a flow has been deployed,
        the client returned will be authorized to run the flow. Stale clients pre-flow-deployment
        will need to call this again in order to run flows.
        """
        if getattr(self, "_flows_client", None) is not None:
            return self._flows_client
        authorizers = self.login_manager.get_manager_authorizers()
        flow_authorizer = authorizers[globus_sdk.FlowsClient.scopes.manage_flows]
        self._flows_client = globus_sdk.FlowsClient(authorizer=flow_authorizer)
        return self._flows_client

    @property
    def specific_flow_client(self) -> globus_sdk.SpecificFlowClient:
        """
        :return: an authorized Gloubs Automate Client. If a flow has been deployed,
        the client returned will be authorized to run the flow. Stale clients pre-flow-deployment
        will need to call this again in order to run flows.
        """
        if getattr(self, "_specific_flow_client", None) is not None:
            return self._specific_flow_client
        authorizers = self.login_manager.get_manager_authorizers()
        flow_authorizer = authorizers.get(self.flow_scope)

        self._specific_flow_client = globus_sdk.SpecificFlowClient(
            self.get_flow_id(), authorizer=flow_authorizer
        )
        return self._specific_flow_client

    def _combine_kw_args(self, kwargs_1: dict, kwargs_2: dict, name: str = None):
        common_args = set(kwargs_1).intersection(set(kwargs_2))
        if common_args:
            ov1, ov2 = {k: kwargs_1[k] for k in common_args}, {
                k: kwargs_2[k] for k in common_args
            }
            log.warning(f"{name} args {ov1} overwritten by explicit args: {ov2}")
        rv_kwargs = copy.deepcopy(kwargs_1)
        rv_kwargs.update(kwargs_2)
        return rv_kwargs

    def refresh_specific_flow_client(self) -> globus_sdk.SpecificFlowClient:
        """
        Destroy the current flows client and return a new one with updated authorizers. This is
        handy in the case where dependent scopes change on a flow, and after login a new client
        is needed.
        """
        self._specific_flow_client = None
        return self.specific_flow_client

    @staticmethod
    def get_flow_checksum(
        flow_definition: dict, flow_schema: dict, flow_kwargs: dict = None
    ):
        """
        Get the SHA256 checksum of the current flow definition.

        :return: sha256 hex string of flow definition
        """

        flow_def = json.dumps(flow_definition, sort_keys=True)
        flow_schema = json.dumps(flow_schema, sort_keys=True)
        flow_kwargs = json.dumps(flow_kwargs or dict(), sort_keys=True)
        data = (flow_def + flow_schema + flow_kwargs).encode()
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

    def get_flow_id(self) -> t.Optional[str]:
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
            self.flow_definition,
            self.flow_schema,
            self.flow_kwargs,
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
        # TODO: The globus sdk does not currently support subscription id on UPDATE.
        # This should change eventually, but right now cannot be supplied or it will raise errors
        # It is added only on CREATE for now.
        # flow_kwargs["subscription_id"] = self.subscription_id
        combine_flow_kwargs = self._combine_kw_args(
            flow_kwargs, self.flow_kwargs, name="Flow"
        )
        if flow_id:
            try:
                log.info(f"Flow checksum failed, updating flow {flow_id}...")
                self.flows_client.update_flow(
                    flow_id,
                    title=self.flow_title,
                    definition=self.flow_definition,
                    **combine_flow_kwargs,
                )
                self.storage.set_value(
                    "flow_checksum",
                    self.get_flow_checksum(
                        self.flow_definition, self.flow_schema, self.flow_kwargs
                    ),
                )
            except globus_sdk.exc.GlobusAPIError as gapie:
                if gapie.http_status == 404 and self.redeploy_on_404:
                    flow_id = None
                else:
                    raise
        if flow_id is None:
            log.info("No flow detected, deploying new flow...")
            flow_kwargs["subscription_id"] = self.subscription_id
            flow = self.flows_client.create_flow(
                self.flow_title, self.flow_definition, **combine_flow_kwargs
            ).data
            log.debug(f'Flow deployed with id {flow["id"]}')
            self.storage.set_value("flow_id", flow["id"])
            self.storage.set_value(
                "flow_checksum",
                self.get_flow_checksum(self.flow_definition, self.flow_schema),
            )
            self.login_manager.add_requirements([flow["globus_auth_scope"]])
            self.refresh_specific_flow_client()

        return flow_id

    def purge_flow(self):
        """
        Remove the stored flow_id and flow_checksum.
        """
        self.storage.del_value("flow_id")
        self.storage.del_value("flow_checksum")

    def run_flow(self, **kwargs):

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

        kwargs = self._combine_kw_args(kwargs, self.run_kwargs, name="Run")
        try:
            flow = self.specific_flow_client.run_flow(**kwargs).data
        except globus_sdk.exc.GlobusAPIError as gapie:
            if gapie.http_status == 404 and self.redeploy_on_404:
                log.warning(
                    f"Flow {self.get_flow_id()} returned 404 and is either deleted or unavailable. "
                    f"Purging flow_id from config file..."
                )
                # On a 404, Gladier can't do anything since it cannot access the old flow.
                # Therefore, purge the old flow and deploy a new one.
                self.purge_flow()
                # Ensure the new flow is deployed
                self.sync_flow()
                # Remake the flow client
                self.refresh_specific_flow_client()
                # Run the flow
                flow = self.specific_flow_client.run_flow(**kwargs).data
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
                        self.refresh_specific_flow_client()
                        log.info("Initiating new login for dependent scope change")
                        flow = self.specific_flow_client.run_flow(**kwargs).data
                    else:
                        raise
                except (TypeError, ValueError):
                    raise gapie from None
            else:
                raise
        log.info(f'Started flow {kwargs.get("label")} with run "{flow["run_id"]}"')

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
        status = self.flows_client.get_run(run_id).data
        try:
            return gladier.utils.automate.get_details(status)
        except (KeyError, AttributeError):
            return status

    @staticmethod
    def _default_progress_callback(response):
        if response["status"] == "ACTIVE":
            print(f'[{response["status"]}]: {response["details"]["description"]}')

    def progress(self, run_id, callback=None, delay=2):
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
            time.sleep(delay)

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
