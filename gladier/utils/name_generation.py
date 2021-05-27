

def get_upper_camel_case(snake_case_name):
    """Make a snake_case_name into UpperCamelCase"""
    return ''.join([nb.capitalize() for nb in snake_case_name.split('_')])


def get_funcx_flow_state_name(funcx_function):
    """State names in Automate are typically upper camel case. This function generates
    an upper case funcx function name for flow states."""
    return get_upper_camel_case(funcx_function.__name__)


def get_funcx_function_name(funcx_function):
    """
    Generate a function name given a funcx function. These function names are used to refer
    to funcx functions within the config. There is no guarantee of uniqueness for function
    names.

    :return: human readable string identifier for a function (intended for a gladier.cfg file)
    """
    return f'{funcx_function.__name__}_funcx_id'


def get_funcx_function_checksum_name(funcx_function):
    """
    Generate a name to refer to the checksum for a given funcx function. Based off of the
    name generated for the function self.get_funcx_function_name. Human readable, intended
    for config.

    :return:  human readable string identifier for a function checksum (for a gladier.cfg file)
    """
    return f'{get_funcx_function_name(funcx_function)}_checksum'
