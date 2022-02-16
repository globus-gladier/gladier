import abc
import logging
import gladier.utils.name_generation

log = logging.getLogger(__name__)


class ToolAlias(abc.ABC):

    input_location = 'input'

    def __init__(self, alias):
        self.alias = alias

    @abc.abstractmethod
    def rename_state(self, state_name, tool):
        return state_name

    @abc.abstractmethod
    def rename_variable(self, variable_name, tool):
        return variable_name

    def get_input_variable(self, flow_input_variable, tool_inputs):
        location = f'$.{self.input_location}.'
        input_name = flow_input_variable.replace(location, '')
        if input_name in tool_inputs:
            return input_name

    def rename_input_variables(self, state_data, tool_inputs, tool):
        if not state_data:
            return
        for k in state_data.keys():
            if isinstance(state_data[k], str):
                input_var = self.get_input_variable(state_data[k], tool_inputs)
                if input_var:
                    new_var = f'$.{self.input_location}.{self.rename_variable(input_var, tool)}'
                    state_data[k] = new_var
            elif isinstance(state_data[k], dict):
                state_data[k] = self.rename_input_variables(state_data[k], tool_inputs, tool)
            elif isinstance(state_data[k], list):
                state_data[k] = [self.rename_input_variables(substate_data, tool_inputs, tool)
                                 for substate_data in state_data[k]]
        return state_data


class NoAlias(ToolAlias):
    def rename_state(self, state_name, tool):
        return state_name

    def rename_variable(self, variable_name, tool):
        return variable_name


class StateSuffixVariablePrefix(ToolAlias):

    def rename_state(self, state_name, tool):
        return f'{state_name}{self.alias}'

    def rename_variable(self, variable_name, tool):
        return f'{gladier.utils.name_generation.get_snake_case(self.alias)}_{variable_name}'
