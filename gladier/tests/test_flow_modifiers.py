import pytest
from gladier.base import GladierBaseTool
from gladier.utils.flow_modifiers import FlowModifiers
from gladier.exc import FlowGenException


def mock_func():
    pass


def mock_func2():
    pass


class MyTool(GladierBaseTool):
    funcx_functions = [mock_func, mock_func2]


def test_basic_modifiers():
    mods = {
        mock_func2: {
            'payload': mock_func,
        }
    }
    fm = FlowModifiers([MyTool()], mods)
    assert len(fm.functions) == 2
    assert len(fm.function_names) == 2
    assert len(fm.state_names) == 2


def test_invalid_modifiers():
    with pytest.raises(FlowGenException):
        FlowModifiers([MyTool()], [])


def test_missing_modifiers():
    mods = {
        'mock_func3': {
            'payload': mock_func,
        }
    }
    with pytest.raises(FlowGenException):
        FlowModifiers([MyTool()], mods)


def test_unsupported_modifiers():
    mods = {
        'mock_func2': {
            'plumbus': mock_func,
        }
    }
    with pytest.raises(FlowGenException):
        FlowModifiers([MyTool()], mods)
