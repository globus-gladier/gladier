import functools
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException
from gladier.utils.flow_generation import generate_tool_flow, combine_tool_flows


def generate_flow_definition(_cls=None, *, modifiers=None):
    """Class decorators for automatically generating flows on either
    GladierBaseTools or GladierClients. For GladierBaseTools, this generates
    a simple flow containing all attached funcx_functions, applying any modifiers
    for custom values the GladierBaseTool needs to run. For GladierClients, this
    instead stitches together all flows defined on GladierBaseTools, in the order
    they are defined for each BaseTool. ``modifiers`` are only allowed on
    GladierBaseTools.

    Example:
    @generate_flow_definition(modifiers={
        my_funcx_function: {
            'payload': '$.MyFuncxFunction.details.result',
            'endpoint': 'funcx_endpoint_non_compute'
        }
    })

    Any modifier values without a preceding '$.' will be replaced with
    a path to general input. The above would result in the following
    for ``funcx_endpoint_non_compute`` above:
        '$.input.funcx_endpoint_non_compute'

    :raises FlowGenException: For a variety of invalid inputs"""
    def decorator_wrapper(cls):
        @functools.wraps(cls)
        def wrapper(*args, **kwargs):
            if issubclass(cls, GladierBaseTool):
                cls.flow_definition = generate_tool_flow(cls, modifiers)
                return cls(*args, **kwargs)
            elif issubclass(cls, GladierBaseClient):
                if modifiers is not None:
                    raise FlowGenException(f'{cls}: Gladier Clients may not '
                                           f'have modifiers.')
                cls.flow_definition = combine_tool_flows(cls)
                return cls(*args, **kwargs)
            else:
                raise FlowGenException(f'Invalid class {cls}, flow generation '
                                       f'only supported for '
                                       f'{[GladierBaseTool, GladierBaseClient]}')

        return wrapper

    if _cls is None:
        return decorator_wrapper
    else:
        return decorator_wrapper(_cls)
