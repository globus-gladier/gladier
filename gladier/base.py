import gladier.utils.tool_alias


class GladierBaseTool(object):
    """Gladier Defaults defines a common method of tying together
    flows, funcx-functions, and default inputs for starting a flow."""

    flow_definition = None
    flow_input = dict()
    required_input = []
    alias_exempt = ['funcx_endpoint_compute', 'funcx_endpoint_noncompute']
    funcx_endpoints = dict()
    funcx_functions = []

    def __init__(self, alias=None, alias_class=None):
        alias_cls = alias_class or gladier.utils.tool_alias.NoAlias
        self.alias_renamer = alias_cls(alias)

    def get_required_input(self):
        return [self.alias_renamer.rename_variable(input_var, self)
                for input_var in self.required_input
                if input_var not in self.alias_exempt]

    def get_flow_input(self):
        return {self.alias_renamer.rename_variable(input_var, self): val
                for input_var, val in self.flow_input.items()
                if input_var not in self.alias_exempt}

    def get_original_inputs(self):
        return [input_var for input_var in set(self.required_input) | set(self.flow_input.keys())
                if input_var not in self.alias_exempt]

    def rename_state(self, state_name, state_data):
        name = self.alias_renamer.rename_state(state_name, self)
        data = self.alias_renamer.rename_input_variables(state_data, self.get_original_inputs(), self)
        return name, data
