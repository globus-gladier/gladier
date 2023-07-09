from gladier import GladierBaseTool, generate_flow_definition


def makedirs(**data):
    """Make a directory on the filesystem"""
    import os
    os.makedirs(data['name'], mode=data['mode'], exist_ok=data['exist_ok'])
    return data['name']


@generate_flow_definition
class MakeDirs(GladierBaseTool):
    """List files on the filesystem"""
    compute_functions = [makedirs]
    required = ['name']
    flow_input = {
        'mode': 0o777,
        'exist_ok': False
    }
