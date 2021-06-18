import pytest
from gladier.utils.flow_compiler import FlowCompiler
from gladier.exc import FlowGenException


def test_valid_flow_ordering(two_step_flow):
    fs = FlowCompiler.get_ordered_flow_states(two_step_flow)
    assert tuple(fs.keys()) == ('MockFunc', 'MockFunc2')


def test_missing_end_attr_raises_error(two_step_flow):
    two_step_flow['States']['MockFunc2'].pop('End')
    with pytest.raises(FlowGenException):
        FlowCompiler.get_ordered_flow_states(two_step_flow)


def test_missing_next_attr_raises_error(two_step_flow):
    two_step_flow['States']['MockFunc'].pop('Next')
    with pytest.raises(FlowGenException):
        FlowCompiler.get_ordered_flow_states(two_step_flow)
