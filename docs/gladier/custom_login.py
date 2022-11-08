from typing import List, Mapping, Union
from globus_sdk import AccessTokenAuthorizer, RefreshTokenAuthorizer
from fair_research_login import NativeClient, LoadError
from gladier import generate_flow_definition, GladierBaseClient, CallbackLoginManager


# A simple shell tool will be used for demonstration
@generate_flow_definition
class GladierTestClient(GladierBaseClient):
    gladier_tools = [
        "gladier_tools.posix.shell_cmd.ShellCmdTool",
    ]


# Fair Research Login is used for simplicity
frl = NativeClient(client_id="7414f0b4-7d05-4bb6-bb00-076fa3f17cf5")

try:
    # Try to use a previous login to avoid a new login flow
    initial_authorizers = frl.get_authorizers_by_scope()
except LoadError:
    # Passing in an empty dict will trigger the callback below
    initial_authorizers = {}


def callback(scopes: List[str]
             ) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
    # 'force' is used for any underlying scope changes. For example, if a flow adds transfer
    # functionality since it was last run, running it again would require a re-login.
    frl.login(requested_scopes=scopes, force=True, refresh_tokens=True)
    return frl.get_authorizers_by_scope()


custom_login_manager = CallbackLoginManager(
    initial_authorizers,
    # If additional logins are needed, the callback is used.
    callback=callback
)

# Pass in any custom login manager to modify the behavior. Everything else stays the same.
client = GladierTestClient(login_manager=custom_login_manager)
run = client.run_flow(flow_input={
    "input": {
        "args": "echo 'Hello Custom Login!'",
        "capture_output": True,
        "funcx_endpoint_compute": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
    }
})

run_id = run['run_id']
client.progress(run_id)
print(f"Flow result: {client.get_status(run_id)['status']}")
