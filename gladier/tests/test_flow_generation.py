import pytest
from gladier.utils.tool_chain import ToolChain
from gladier.exc import FlowGenException


def test_valid_flow_ordering(two_step_flow):
    tc = ToolChain.get_ordered_flow_states(two_step_flow)
    assert tuple(tc.keys()) == ('MockFunc', 'MockFunc2')


def test_missing_end_attr_raises_error(two_step_flow):
    two_step_flow['States']['MockFunc2'].pop('End')
    with pytest.raises(FlowGenException):
        ToolChain.get_ordered_flow_states(two_step_flow)


def test_missing_next_attr_raises_error(two_step_flow):
    two_step_flow['States']['MockFunc'].pop('Next')
    with pytest.raises(FlowGenException):
        ToolChain.get_ordered_flow_states(two_step_flow)
