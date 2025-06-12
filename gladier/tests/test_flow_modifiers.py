import pytest
from gladier.base import GladierBaseTool
from gladier.flow_builder.compute import ComputeFlowBuilderv2
from gladier.exc import FlowGenException


def mock_func():
    pass


def mock_func2():
    pass


class MyTool(GladierBaseTool):
    compute_functions = [mock_func, mock_func2]


def test_basic_modifiers():
    mods = {
        mock_func2: {
            "payload": mock_func,
        }
    }
    builder = ComputeFlowBuilderv2(MyTool())
    fd = builder.apply_modifiers(mods, builder.get_flow_definition())
    assert len(fd["States"]) == 2
    assert (
        fd["States"]["MockFunc2"]["Parameters"]["tasks"][0]["payload.$"]
        == "$.MockFunc.details.results"
    )


def test_invalid_modifiers():
    builder = ComputeFlowBuilderv2(MyTool())
    with pytest.raises(FlowGenException):
        builder.apply_modifiers([], builder.get_flow_definition())


def test_missing_modifiers():
    mods = {
        "mock_func3": {
            "payload": mock_func,
        }
    }
    builder = ComputeFlowBuilderv2(MyTool())
    with pytest.raises(FlowGenException):
        builder.apply_modifiers(mods, builder.get_flow_definition())


def test_unsupported_modifiers():
    mods = {
        "mock_func2": {
            "plumbus": mock_func,
        }
    }
    builder = ComputeFlowBuilderv2(MyTool())
    with pytest.raises(FlowGenException):
        builder.apply_modifiers(mods, builder.get_flow_definition())


def test_duplicated_tools():
    builder = ComputeFlowBuilderv2(MyTool())

    mods = {"mock_func2": {"payload": "mock_func"}}
    flow_definition = {
        "States": {
            "MockFunc": {"Parameters": {"tasks": [{"payload": "foo"}]}},
            "MockFunc2": {"Parameters": {"tasks": [{"payload": "bar"}]}},
        }
    }

    builder.apply_modifiers(mods, flow_definition)
    mock2_pl = flow_definition["States"]["MockFunc2"]["Parameters"]["tasks"][0][
        "payload.$"
    ]
    assert mock2_pl == "$.MockFunc.details.results"
