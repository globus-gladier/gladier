import logging
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException
from gladier.utils.flow_modifiers import FlowModifiers
from gladier.utils.name_generation import (
    get_funcx_flow_state_name,
    get_funcx_function_name
)
from gladier.utils.tool_chain import ToolChain


log = logging.getLogger(__name__)


def combine_tool_flows(client: GladierBaseClient, modifiers):
    """
    Combine flow definitions on each of a Gladier Client's **tools** and return
    a single flow definition that runs each state in order from first to last.

    Modifiers can be applied to any of the states within the flow.
    """
    flow_moder = FlowModifiers(client.tools, modifiers, cls=client)
    chain = ToolChain(flow_comment=client.__doc__).chain(client.tools)
    return flow_moder.apply_modifiers(chain.flow_definition)


def generate_tool_flow(tool: GladierBaseTool, modifiers):
    """Generate a flow definition for a Gladier Tool based on the defined ``funcx_functions``.
    Accepts modifiers for funcx functions"""

    flow_moder = FlowModifiers([tool], modifiers, cls=tool)

    tools = ToolChain()
    for fx_func in tool.funcx_functions:
        tools.chain_state(*generate_funcx_flow_state(fx_func))

    flow = tools.flow_definition
    if not flow['States']:
        raise FlowGenException(f'Tool {tool} has no flow states. Add a list of python functions '
                               f'as "{tool}.funcx_functions = [myfunction]" or set a custom flow '
                               f'definition instead using `{tool}.flow_definition = mydef`')
    return flow_moder.apply_modifiers(flow)


def generate_funcx_flow_state(funcx_function):
    state_name = get_funcx_flow_state_name(funcx_function)

    return state_name, {
        'Comment': funcx_function.__doc__,
        'Type': 'Action',
        'ActionUrl': 'https://automate.funcx.org',
        'ActionScope': 'https://auth.globus.org/scopes/'
                       'b3db7e59-a6f1-4947-95c2-59d6b7a70f8c/action_all',
        'ExceptionOnActionFailure': False,
        'Parameters': {
            'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_compute',
                'function.$': f'$.input.{get_funcx_function_name(funcx_function)}',
                'payload.$': '$.input',
            }]
        },
        'ResultPath': f'$.{state_name}',
        'WaitTime': 300,
    }
