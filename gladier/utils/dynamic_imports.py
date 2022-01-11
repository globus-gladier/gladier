from importlib import import_module


def parse_alias(dotted_string_path):
    if ':' in dotted_string_path:
        return dotted_string_path.rsplit(':', 1)
    return dotted_string_path, None


def import_string(dotted_string_path):
    dotted_string_path, _ = parse_alias(dotted_string_path)
    module_paths = dotted_string_path.rsplit('.', 1)
    if len(module_paths) != 2:
        raise ImportError(f'Path "{dotted_string_path} must be a dotted path')
    module_path, class_name = module_paths
    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as ae:
        raise ImportError(f'Failed to import {class_name} from {module}.') from ae
