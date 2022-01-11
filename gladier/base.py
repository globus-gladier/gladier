
class GladierBaseTool(object):
    """Gladier Defaults defines a common method of tying together
    flows, funcx-functions, and default inputs for starting a flow."""

    flow_definition = None
    flow_input = dict()
    required_input = []
    funcx_endpoints = dict()
    funcx_functions = []

    def __init__(self, alias=None):
        self.alias = alias
