import logging
import json
import copy
from collections import OrderedDict
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException
from gladier.utils.flow_modifiers import FlowModifiers
from gladier.utils.name_generation import (
    get_funcx_flow_state_name,
    get_funcx_function_name
)


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

    flow_def = combine_flow_states(tool, flow_states)
    flow_def = flow_moder.apply_modifiers(flow_def)
    return json.loads(json.dumps(flow_def))


def combine_flow_states(cls, flow_states):
    """
    Given a GlaiderBaseClient or GladierBaseTool, generate a complete automate flow.
    """
    keylist = list(flow_states.keys())
    first, last = keylist[0], keylist[-1]
    flow_definition = OrderedDict([
        ('Comment', cls.__doc__),
        ('StartAt', first),
        ('States', flow_states)
    ])

    for fs_data in flow_states.values():
        if fs_data.get('End'):
            fs_data.pop('End')

    # Set the order for each of the flow states. Order is linear, based
    # on the order of the funcx functions defined in the tool
    for state_name, state_data in flow_states.items():
        if state_name == last:
            state_data['End'] = True
        else:
            next_index = keylist.index(state_name) + 1
            state_data['Next'] = keylist[next_index]
    if not flow_definition['Comment']:
        state_names = ", ".join(flow_definition["States"].keys())
        flow_definition['Comment'] = f'Flow with states: {state_names}'

    return flow_definition


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


def get_ordered_flow_states(flow_definition):
    flow_def = copy.deepcopy(flow_definition)
    ordered_states = OrderedDict()
    state = flow_def['StartAt']
    while state is not None:
        ordered_states[state] = flow_def['States'][state]
        if flow_def['States'][state].get('Next'):
            state = flow_def['States'][state].get('Next')
        elif flow_def['States'][state].get('End') is True:
            break
        else:
            raise FlowGenException(f'Flow definition has no "Next" or "End" for state "{state}" '
                                   f'with states: {flow_def["States"].keys()}')

    ordered_states[state] = flow_def['States'][state]
    return ordered_states
