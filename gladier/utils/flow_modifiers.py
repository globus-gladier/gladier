import logging
from gladier.exc import FlowModifierException
from gladier.utils.name_generation import get_funcx_flow_state_name

log = logging.getLogger(__name__)


class FlowModifiers:
    supported_modifiers = {'endpoint', 'payload'}
    funcx_modifiers = {'endpoint', 'payload'}

    def __init__(self, tools, modifiers, cls=None):
        self.cls = cls
        self.tools = tools
        self.functions = [func for tool in tools for func in tool.funcx_functions]
        self.function_names = [f.__name__ for f in self.functions]
        self.state_names = [get_funcx_flow_state_name(f) for f in self.functions]
        self.modifiers = modifiers

    def get_function(self, function_identifier):
        if function_identifier in self.function_names:
            return self.functions[self.function_names.index(function_identifier)]
        if function_identifier in self.functions:
            return function_identifier

    def get_state_result_path(self, state_name):
        return f'$.{state_name}.details.results'

    def check_modifiers(self):
        if not isinstance(self.modifiers, dict):
            raise FlowModifierException(f'{self.cls}: Flow Modifiers must be a dict')

        # Check if modifiers were set correctly
        for name, mods in self.modifiers.items():
            if not self.get_function(name):
                raise FlowModifierException(f'Class {self.cls} included modifier which does not '
                                            f'exist: {name}. Allowed modifiers include '
                                            f'{", ".join(self.function_names)}')

            for mod_name, mod_value in mods.items():
                if mod_name not in self.supported_modifiers:
                    raise FlowModifierException(f'Class {self.cls}: Unsupported modifier "{mod_name}". '
                                                f'The only supported modifiers are: '
                                                f'{self.supported_modifiers}')

    def apply_modifiers(self, flow):
        for name, mods in self.modifiers.items():
            state_name = get_funcx_flow_state_name(name)
            flow['States'][state_name] = self.apply_modifier(flow['States'][state_name], mods)
        return flow

    def apply_modifier(self, flow_state, state_modifiers):

        for modifier_name, value in state_modifiers.items():
            # If this is for a funcx task
            if modifier_name in self.funcx_modifiers:
                flow_state['Parameters']['tasks'] = [
                    self.generic_set_modifier(fx_task, modifier_name, value)
                    for fx_task in flow_state['Parameters']['tasks']
                ]
        return flow_state

    def generic_set_modifier(self, item, mod_name, mod_value):
        if not isinstance(mod_value, str):
            if mod_value in self.functions:
                sn = get_funcx_flow_state_name(mod_value)
                mod_value = self.get_state_result_path(sn)
        elif isinstance(mod_value, str) and not mod_value.startswith('$.'):
            if mod_value in self.function_names:
                sn = self.state_names[self.function_names.index(mod_value)]
                mod_value = self.get_state_result_path(sn)
            elif mod_value in self.state_names:
                mod_value = self.get_state_result_path(mod_value)
            else:
                mod_value = f'$.input.{mod_value}'

        mod_name = f'{mod_name}.$'
        if mod_value.startswith('$.'):
            item[mod_name] = mod_value
        else:
            item[mod_name] = mod_value
        log.debug(f'Set modifier {mod_name} to {mod_value}')
        return item
