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


def test_duplicated_tools():
    fm = FlowModifiers([MyTool(), MyTool()], {
        'mock_func2': {
            'payload': 'mock_func'
        }
    })
    new_flow = fm.apply_modifiers({
        'States': {
            'MockFunc': {'Parameters': {'tasks': [{'payload': 'foo'}]}},
            'MockFunc2': {'Parameters': {'tasks': [{'payload': 'bar'}]}},
        }
    })
    mock2_pl = new_flow['States']['MockFunc2']['Parameters']['tasks'][0]['payload.$']
    assert mock2_pl == '$.MockFunc.details.results'
