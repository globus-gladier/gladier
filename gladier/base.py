from .client import GladierBaseClient


class GladierBaseTool(object):
    """Gladier Defaults defines a common method of tying together
    flows, funcx-functions, and default inputs for starting a flow."""

    flow_definition = None
    required_input = []
    funcx_endpoints = dict()
    funcx_functions = []

    def check_endpoints(self):
        pass

    def check_globus(self):
        pass


class GladierBaseContainer(object):

    container_url = None
    container_type = None
    container_location = None
    container_flags = None

    def check_existance(self):
        pass