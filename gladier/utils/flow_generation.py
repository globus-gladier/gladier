import logging
import json
from collections import OrderedDict
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException
from gladier.utils.flow_modifiers import FlowModifiers
from gladier.utils.name_generation import (
    get_funcx_flow_state_name,
    get_funcx_function_name
)
from gladier.utils.flow_compiler import FlowCompiler


log = logging.getLogger(__name__)


def combine_tool_flows(client: GladierBaseClient, modifiers):
    """
    Combine flow definitions on each of a Gladier Client's **tools** and return
    a single flow definition that runs each state in order from first to last.

    Modifiers can be applied to any of the states within the flow.
    """
    flow_moder = FlowModifiers(client.tools, modifiers, cls=client)

    flow_states = OrderedDict()
    for tool in client.tools:
        if tool.flow_definition is None:
            raise FlowGenException(f'Tool {tool} did not set .flow_definition attribute or set '
                                   f'@generate_flow_definition (funcx functions only). Please '
                                   f'set a flow definition for {tool.__class__.__name__}.')
        states = get_ordered_flow_states(tool.flow_definition)
        flow_states.update(states)

    flow_def = combine_flow_states(client, flow_states)
    flow_def = flow_moder.apply_modifiers(flow_def)
    return json.loads(json.dumps(flow_def))


def generate_tool_flow(tool: GladierBaseTool, modifiers):
    """Generate a flow definition for a Gladier Tool based on the defined ``funcx_functions``.
    Accepts modifiers for funcx functions"""

    flow_moder = FlowModifiers([tool], modifiers, cls=tool)

    flow_states = OrderedDict()
    for fx_func in tool.funcx_functions:
        fx_state = generate_funcx_flow_state(fx_func)
        flow_states.update(fx_state)

    if not flow_states:
        raise FlowGenException(f'Tool {tool} has no flow states. Add a list of python functions '
                               f'as "{tool}.funcx_functions = [myfunction]" or set a custom flow '
                               f'definition instead using `{tool}.flow_definition = mydef`')
    flow_def = FlowCompiler.combine_flow_states(flow_states, flow_comment=tool.__doc__)
    flow_def = flow_moder.apply_modifiers(flow_def)
    return json.loads(json.dumps(flow_def))


def generate_funcx_flow_state(funcx_function):

    state_name = get_funcx_flow_state_name(funcx_function)
    tasks = [OrderedDict([
        ('endpoint.$', '$.input.funcx_endpoint_compute'),
        ('function.$', f'$.input.{get_funcx_function_name(funcx_function)}'),
        ('payload.$', '$.input'),
    ])]
    flow_state = OrderedDict([
        ('Comment', funcx_function.__doc__),
        ('Type', 'Action'),
        ('ActionUrl', 'https://automate.funcx.org'),
        ('ActionScope', 'https://auth.globus.org/scopes/'
                        'b3db7e59-a6f1-4947-95c2-59d6b7a70f8c/action_all'),
        ('ExceptionOnActionFailure', False),
        ('Parameters', OrderedDict(tasks=tasks)),
        ('ResultPath', f'$.{state_name}'),
        ('WaitTime', 300),
    ])
    return OrderedDict([(state_name, flow_state)])
