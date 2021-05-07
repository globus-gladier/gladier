import logging
from collections import OrderedDict
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException


log = logging.getLogger(__name__)


def combine_tool_flows(cls: GladierBaseClient):
    flow_states = OrderedDict()
    for tool in cls().tools:
        flow_states.update(tool.flow_definition['States'])

    return generate_flow_definition(cls, flow_states)


def generate_tool_flow(cls, modifiers):
    if not issubclass(cls, GladierBaseTool):
        raise FlowGenException(f'{cls} is not of type {GladierBaseTool}!')

    # Check if modifiers were set correctly
    modifier_names = set(m.__name__ for m in modifiers.keys())
    func_names = set(f.__name__ for f in cls.funcx_functions)
    fdiff = modifier_names.difference(func_names)
    if fdiff:
        raise FlowGenException(f'Class {cls} included modifiers for functions'
                               f'which don\'t exist: {fdiff}')

    flow_states = OrderedDict()
    for fx_func in cls.funcx_functions:
        fx_state = generate_funcx_flow_state(fx_func, modifiers)
        flow_states.update(fx_state)

    return generate_flow_definition(cls, flow_states)


def generate_flow_definition(cls, flow_states):
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

    return flow_definition


def generate_funcx_flow_state_name(funcx_function):
    name_bits = funcx_function.__name__.split('_')
    name_bits_capitalized = [nb.capitalize() for nb in name_bits]
    return ''.join(name_bits_capitalized)


def generate_funcx_flow_state(funcx_function, modifiers):
    fname = funcx_function.__name__
    supported_modifiers = {'endpoint', 'payload'}
    fx_modifiers = modifiers.get(funcx_function, {})
    if fx_modifiers:
        unsupported_mods = set(modifiers[funcx_function].keys()).difference(supported_modifiers)
        if unsupported_mods:
            raise FlowGenException(f'Modifiers for function {fname} are unsupported: '
                                   f'{unsupported_mods}')

    log.info(f'Function "{fname}", applying modifiers: {list(fx_modifiers.keys())}')

    state_name = generate_funcx_flow_state_name(funcx_function)
    tasks = [OrderedDict([
        ('endpoint.$', '$.input.funcx_endpoint_compute'),
        ('func.$', f'$.input.{GladierBaseClient.get_funcx_function_name(funcx_function)}'),
        ('payload.$', '$.input'),
    ])]
    for task in tasks:
        for key in task.keys():
            modifier = fx_modifiers.get(key.rstrip('.$'))
            if modifier:
                if not modifier.startswith('$.'):
                    modifier = f'$.input.{modifier}'
                task[key] = modifier
                log.debug(f'{fname}: Set modifier "{key}" to "{modifier}"')

    flow_state = OrderedDict([
        ('Comment', funcx_function.__doc__),
        ('Type', 'Action'),
        ('ActionUrl', 'https://api.funcx.org/automate'),
        ('ActionScope', 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2'),
        ('ExceptionOnActionFailure', False),
        ('Parameters', OrderedDict(tasks=tasks)),
        ('ResultPath', f'$.{state_name}'),
        ('WaitTime', 300),
    ])
    return OrderedDict([(state_name, flow_state)])
