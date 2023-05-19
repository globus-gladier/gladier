import logging
import typing
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException
from gladier.utils.flow_modifiers import FlowModifiers
from gladier.utils.name_generation import (
    get_compute_flow_state_name,
    get_compute_function_name
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


def _get_duplicate_functions(compute_functions: typing.List[callable]):
    tracked_set = set()
    func_names = [get_compute_flow_state_name(f) for f in compute_functions]
    return [f for f in func_names if f in tracked_set or tracked_set.add(f)]


def _fix_old_tools(tool):
    funcx_functions = getattr(tool, 'funcx_functions', None)
    compute_functions = getattr(tool, 'compute_functions', None)

    if funcx_functions and not compute_functions:
        log.warning(f'Tool {tool} defines attributue "funcx_functions" which has now been '
                    'changed to "compute_functions". Automatically configuring compute_functions '
                    f'for new tool. Please update the old tool {tool}')
        setattr(tool, 'compute_functions', funcx_functions)


def generate_tool_flow(tool: GladierBaseTool, modifiers):
    """Generate a flow definition for a Gladier Tool based on the defined ``compute_functions``.
    Accepts modifiers for compute functions"""
    _fix_old_tools(tool)

    duplicate_functions = _get_duplicate_functions(tool.compute_functions)
    if duplicate_functions:
        raise FlowGenException(f'Tool {tool} contains duplicate function names: '
                               f'{duplicate_functions}')

    flow_moder = FlowModifiers([tool], modifiers, cls=tool)

    tools = ToolChain()
    for fx_func in tool.compute_functions:
        tools.chain_state(*generate_compute_flow_state(fx_func))

    flow = tools.flow_definition
    if not flow['States']:
        raise FlowGenException(f'Tool {tool} has no flow states. Add a list of python functions '
                               f'as "{tool}.compute_functions = [myfunction]" or set a custom flow '
                               f'definition instead using `{tool}.flow_definition = mydef`')
    return flow_moder.apply_modifiers(flow)


def generate_compute_flow_state(compute_function):
    state_name = get_compute_flow_state_name(compute_function)

    return state_name, {
        'Comment': compute_function.__doc__,
        'Type': 'Action',
        'ActionUrl': 'https://compute2.dev.funcx.org/fxap',
        'ExceptionOnActionFailure': False,
        'Parameters': {
            'tasks': [{
                'endpoint.$': '$.input.compute_endpoint',
                'function.$': f'$.input.{get_compute_function_name(compute_function)}',
                'payload.$': '$.input',
            }]
        },
        'ResultPath': f'$.{state_name}',
        'WaitTime': 300,
    }
