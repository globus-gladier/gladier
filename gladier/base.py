from .client import GladierClient as GladierBaseClient

##not sure how to update this.
# class GladierBaseClient(GladierClient):

#     container_url = None
#     container_type = None
#     container_location = None
#     container_flags = None

class GladierBaseTool(object):
    """Gladier Defaults defines a common method of tying together
    flows, funcx-functions, and default inputs for starting a flow."""

    flow_definition = None

    required_input = []
    
    funcx_endpoints = dict()
    funcx_functions = []



class GladierBaseContainer(object):

    container_url = None
    container_type = None
    container_location = None
    container_flags = None

