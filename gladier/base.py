import copy
from typing import List, Mapping, Any
from gladier.utils.tool_alias import ToolAlias
from gladier.utils.flow_traversal import iter_flow


class GladierBaseTool(object):
    """Gladier Defaults defines a common method of tying together
    flows, funcx-functions, and default inputs for starting a flow."""

    flow_definition = None
    flow_input = dict()
    flow_transition_states = []
    required_input = []
    alias_exempt = ['funcx_endpoint_compute', 'funcx_endpoint_non_compute']
    funcx_endpoints = dict()
    funcx_functions = []

    def __init__(self, alias: str = None, alias_class: ToolAlias = None):
        self.alias = alias
        alias_cls = alias_class
        if alias and not alias_class:
            raise ValueError(
                f'{self.__class__.__name__} given alias "{alias}" but not "alias_class". '
                'ex: alias_class=gladier.utils.tool_alias.StateSuffixVariablePrefix'
            )
        if alias_class:
            self.alias_renamer = alias_cls(alias)

    def get_required_input(self) -> List[str]:
        if self.alias:
            required = []
            for input_var in self.required_input:
                if input_var not in self.alias_exempt:
                    required.append(self.alias_renamer.rename_variable(input_var, self))
                else:
                    required.append(input_var)
            return required
        else:
            return self.required_input

    def get_flow_input(self) -> Mapping[str, Any]:
        if not self.alias:
            return self.flow_input
        flow_input = dict()
        for input_var, val in self.flow_input.items():
            if input_var not in self.alias_exempt:
                flow_input[self.alias_renamer.rename_variable(input_var, self)] = val
            else:
                flow_input[input_var] = val
        return flow_input

    def get_flow_transition_states(self) -> List[str]:
        return self.flow_transition_states

    def get_original_inputs(self) -> Mapping[str, Any]:
        return [input_var for input_var in set(self.required_input) | set(self.flow_input.keys())
                if input_var not in self.alias_exempt]

    def rename_state(self, state_name: str, state_data: Mapping[str, Any]) -> Mapping[str, Any]:
        name = self.alias_renamer.rename_state(state_name, self)
        data = self.alias_renamer.rename_input_variables(state_data,
                                                         self.get_original_inputs(), self)
        return name, data

    def get_flow_definition(self) -> Mapping[str, Any]:

        if not self.alias:
            return self.flow_definition

        new_states = {}
        for state_name, state_data in iter_flow(self.flow_definition):
            new_name, new_state = self.rename_state(state_name, state_data)
            new_states[new_name] = new_state
            if new_state.get('Next'):
                new_state['Next'] = self.alias_renamer.rename_state(new_state['Next'], self)
            if new_state['Type'] == 'Choice':
                for choice in new_state['Choices']:
                    if choice.get('Next'):
                        choice['Next'] = self.alias_renamer.rename_state(choice['Next'], self)

        new_flow_def = copy.deepcopy(self.flow_definition)
        new_flow_def['States'] = new_states
        new_flow_def['StartAt'] = self.alias_renamer.rename_state(self.flow_definition['StartAt'],
                                                                  self)
        return new_flow_def
