import pytest
from gladier.exc import FlowGenException
from gladier.utils.flow_traversal import iter_flow, get_end_states


def test_iter_flow(two_step_flow):
    names = [name for name, state in iter_flow(two_step_flow)]
    assert len(names) == 2
    assert list(names) == ['MockFunc', 'MockFunc2']


def test_get_end_states(two_step_flow):
    states = list(get_end_states(two_step_flow))
    assert len(states) == 1
    assert list(states) == ['MockFunc2']


def test_flow_branch():
    branch_flow = {
        'StartAt': '1A',
        'States': {
            '1A': {
                'Type': 'Choice',
                'Default': '2A',
                'Choices': [{
                    'Next': '1B',
                    'Variable': '$.foo',
                    'Exists': True,
                }]
            },
            '2A': {
                'Type': 'Pass',
                'End': 'True'
            },
            '1B': {
                'Type': 'Pass',
                'End': 'True',
            }
        }
    }
    states = set(get_end_states(branch_flow))
    assert len(states) == 2
    assert set(states) == {'2A', '1B'}


def test_flow_cycle_in_choice():
    branch_flow = {
        'StartAt': '1A',
        'States': {
            '1A': {
                'Type': 'Pass',
                'Next': '2A',
            },
            '2A': {
                'Type': 'Choice',
                'Default': '1B',
                'Choices': [{
                    'Next': '1A',
                    'Variable': '$.foo',
                    'Exists': True,
                }]
            },
            '1B': {
                'Type': 'Pass',
                'End': 'True'
            },
        }
    }
    states = list(get_end_states(branch_flow))
    assert len(states) == 1
    assert list(states) == ['1B']


def test_flow_cycle_default():
    branch_flow = {
        'StartAt': '1A',
        'States': {
            '1A': {
                'Type': 'Pass',
                'Next': '2A',
            },
            '2A': {
                'Type': 'Choice',
                'Default': '1A',
                'Choices': [{
                    'Next': '1B',
                    'Variable': '$.foo',
                    'SufficientlyDone': True,
                }]
            },
            '1B': {
                'Type': 'Pass',
                'End': 'True'
            },
        }
    }
    states = set(get_end_states(branch_flow))
    assert len(states) == 1
    assert states == {'1B'}


def test_multi_branch_cycle():
    branch_flow = {
        'StartAt': '1A',
        'States': {
            '1A': {
                'Type': 'Pass',
                'Next': '2A',
            },
            '2A': {
                'Type': 'Choice',
                'Default': '3A',
                'Choices': [{
                    'Next': '1B',
                    'Variable': '$.foo',
                    'SufficientlyDone': True,
                }, {
                    'Next': '1C',
                    'Variable': '$.foo',
                    'SufficientlyDone': True,
                }]
            },
            '3A': {
                'Type': 'Pass',
                'End': True
            },
            '1B': {
                'Type': 'Choice',
                'Default': '1A',
                'Choices': [{
                    'Next': '2B',
                    'Variable': '$.foo',
                    'SufficientlyDone': True,
                }, {
                    'Next': '1C',
                    'Variable': '$.foo',
                    'SufficientlyDone': True,
                }]
            },
            '2B': {
                'Type': 'Pass',
                'Next': '1A',
            },
            '1C': {
                'Type': 'Pass',
                'End': True,
            },


        }
    }
    states = list(get_end_states(branch_flow))
    assert len(states) == 2
    assert set(states) == {'3A', '1C'}


def test_state_does_not_exist():
    flow = {
        'StartAt': '1A',
        'States': {
            '1A': {
                'Type': 'Pass',
                'Next': '2A',
            },
            '3A': {
                'Type': 'Pass',
                'End': True,
            },
        }
    }
    with pytest.raises(FlowGenException):
        list(get_end_states(flow))
