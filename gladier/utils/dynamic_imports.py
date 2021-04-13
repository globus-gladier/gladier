from importlib import import_module


def import_string(string_path):
    module_paths = string_path.rsplit('.', 1)
    if len(module_paths) != 2:
        raise ImportError(f'Path "{string_path} must be a dotted path')
    module_path, class_name = module_paths

    try:
        module = import_module(module_path)
        return getattr(module, class_name)
    except AttributeError as ae:
        raise ImportError(f'Failed to import {class_name} from {module}.') from ae
