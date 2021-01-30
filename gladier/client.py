import os
import logging

import fair_research_login
import globus_automate_client
from funcx import FuncXClient
from funcx.serialize import FuncXSerializer

import gladier
import gladier.config
import gladier.dynamic_imports
import gladier.exc
log = logging.getLogger(__name__)


class GladierClient(object):
    """The CfdeClient enables easily using the CFDE tools to ingest data."""
    secret_config_filename = os.path.expanduser("~/.gladier-secrets.cfg")
    config_filename = 'gladier.cfg'
    app_name = 'gladier_client'
    client_id = None

    def __init__(self, authorizers=None):
        self.__config = None
        self.authorizers = authorizers
        self.__flows_client = None

    @property
    def version(self):
        return VERSION

    @property
    def config(self):
        if getattr(self, '__config', None) is not None:
            return self.__config
        log.debug(f'Creating new Gladier Config: {self.config_filename}')
        self.__config = gladier.config.GladierConfig(filename=self.config_filename)
        return self.__config

    def get_native_client(self):
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

    def login(self, **login_kwargs):
        """Login to the cfde-submit client. This will ensure the user has the correct
        tokens configured but it DOES NOT guarantee they are in the correct group to
        run a flow. Can be run both locally and on a server.
        See help(fair_research_login.NativeClient.login) for a full list of kwargs.
        """
        nc = self.get_native_client()
        log.info("Initiating Native App Login...")
        log.debug(f"Requesting Scopes: {self.scopes}")
        login_kwargs["requested_scopes"] = login_kwargs.get("requested_scopes", self.scopes)
        nc.login(**login_kwargs)
        self.authorizers = nc.get_authorizers_by_scope()

    def logout(self):
        """Log out and revoke this client's tokens. This object will no longer
        be usable; to submit additional data or check the status of previous submissions,
        you must create a new CfdeClient.
        """
        if not self.client_id:
            raise gladier.exc.AuthException('Gladier client must be instantiated with a '
                                    '"client_id" to use "login()!')
        self.__native_client.logout()

    def is_logged_in(self):
        try:
            return bool(self.authorizers)
        except gladier.exc.NotLoggedIn:
            return False

    @property
    def scopes(self):
        gladier_scopes = list(globus_automate_client.flows_client.ALL_FLOW_SCOPES)
        # Set to funcx_scope = FuncXClient.FUNCX_SCOPE in funcx==0.0.6
        gladier_scopes.append('https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all')
        flow_scope = self.config['DEFAULT'].get('flow_scope')
        if flow_scope:
            gladier_scopes.append(flow_scope)
        return gladier_scopes

    @property
    def flows_client(self):
        if getattr(self, '__flows_client', None) is not None:
            return self.__flows_client
        automate_authorizer = self.authorizers[globus_automate_client.flows_client.MANAGE_FLOWS_SCOPE]

        def get_flow_authorizer(*args, **kwargs):
            return automate_authorizer

        self.__flows_client = globus_automate_client.FlowsClient.new_client(
            self.client_id, get_flow_authorizer, automate_authorizer,
        )
        return self.__flows_client

    def get_gladier_defaults(self, import_string):
        default_cls = gladier.dynamic_imports.import_string(self.flow_definition)
        default_inst = default_cls()
        if isinstance(default_inst, gladier.defaults.GladierDefaults):
            return default_inst
        raise gladier.exc.ConfigException(f'"{import_string}" must be a dict or a dotted import string ')

    def get_flow_definition(self):
        if getattr(self, 'flow_definition', None):
            raise gladier.exc.ConfigException(f'"flow_definition" was not set on {foo.__class__.__name__}')

        if isinstance(self.flow_definition, dict):
            return self.flow_definition
        elif isinstance(flow_def, str):
            return self.get_gladier_defaults(self.flow_definition).flow_definition
        raise gladier.exc.ConfigException(f'"flow_definition" must be a dict or an import string '
                                  f'to a sub-class of type '
                                  f'"gladier.defaults.GladierDefaults"')

    def register_funcx_functions(self, functions):
        """Register the functions with funcx and store their ids"""
        fxs = FuncXSerializer()
        registered_functions = {}
        for func in functions:
            fname, fserialized = f'{func.__name__}_funcx_id', fxs.serialize(func)
            fchecksum = hashlib.sha256(fserialized.encode()).hexdigest()
            if self.config.get(f'{fname}_checksum') != fchecksum or not self.config.get(fname):
                log.info(f'Re-registering function {fname}')
                self.config['DEFAULT'][fname] = self.fxc.register_function(func, func.__doc__)
                self.config['DEFAULT'][f'{fname}_checksum'] = fchecksum
                self.config.save()
            registered_functions[fname] = self.config['DEFAULT'][fname]
        return registered_functions

    def check_flow(self, flow_id, register=True):
        """Register the automate flow and store its id and scope"""
        fc = self.flows_client()
        flow_definition = self.get_flow_definition()
        flow_checksum = hashlib.sha256(json.dumps(flow_definition).encode()).hexdigest()

        if flow_id and self.config.get('automate_scope'):
            if self.config.get('automate_flow_checksum') == flow_checksum:
                log.debug('Flow Checksum matches, using existing flow.')
                return

        if flow_id:
            try:
                log.info(f'Flow checksum failed, updating flow {flow_id}...')
                fc.update_flow(flow_id, flow_definition)
            except globus_sdk.exc.GlobusAPIError as gapie:
                if gapie.code == 'Not Found':
                    flow_id = None
        if flow_id is None:
            log.info('No flow detected, deploying new flow...')
            flow = fc.deploy_flow(flow_definition, title="XPCS Flow")
            self.config['DEFAULT']['automate_flowid'] = flow['id']
            self.config['DEFAULT']['automate_scope'] = flow['globus_auth_scope']
        self.config['DEFAULT']['automate_flow_checksum'] = flow_checksum
        self.config.save()

    def get_input(self, register=True):
        if getattr(self, 'tools', None) is None:
            raise gladier.exc.ConfigException('"tools" must be a list of Gladier Tools')
        flow_input = {}
        for import_string in self.tools:
            defaults = self.get_gladier_defaults(import_string)
            flow_input.update(self.register_funcx_functions(defaults.funcx_functions))
            flow_input.update(defaults.flow_input)
        return flow_input

    def start_flow(self, flow_input=None):
        combine_flow_input = self.get_input()
        combine_flow_input.update(flow_input or dict())
        return self.flows_client.run_flow(self.config['DEFAULT']['automate_flowid'],
                                          self.config['DEFAULT']['automate_scope'],
                                          combine_flow_input).data
