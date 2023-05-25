import re


def get_upper_camel_case(snake_case_name):
    """Make a snake_case_name into UpperCamelCase"""
    return ''.join([nb.capitalize() for nb in snake_case_name.split('_')])


def get_snake_case(upper_camel_case):
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    snake_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', upper_camel_case)
    snake_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_name).lower()
    return snake_name


def get_compute_flow_state_name(compute_function):
    """State names in Automate are typically upper camel case. This function generates
    an upper case compute function name for flow states."""
    return get_upper_camel_case(compute_function.__name__)


def get_compute_function_name(compute_function):
    """
    Generate a function name given a compute function. These function names are used to refer
    to compute functions within the config. There is no guarantee of uniqueness for function
    names.

    :return: human readable string identifier for a function (intended for a gladier.cfg file)
    """
    return f'{compute_function.__name__}_function_id'


def get_compute_function_checksum_name(compute_function):
    """
    Generate a name to refer to the checksum for a given compute function. Based off of the
    name generated for the function self.get_compute_function_name. Human readable, intended
    for config.

    :return:  human readable string identifier for a function checksum (for a gladier.cfg file)
    """
    return f'{get_compute_function_name(compute_function)}_checksum'
