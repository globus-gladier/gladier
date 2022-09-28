from gladier.utils.flow_traversal import iter_flow, get_end_states


def test_iter_flow(two_step_flow):
    names = [name for name, state in iter_flow(two_step_flow)]
    assert len(names) == 2
    assert list(names) == ['MockFunc', 'MockFunc2']


def test_get_end_states(two_step_flow):
    states = list(get_end_states(two_step_flow))
    assert len(states) == 1
    assert list(states) == ['MockFunc2']
