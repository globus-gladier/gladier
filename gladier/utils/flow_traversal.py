import logging
from typing import Mapping, Any, List, Iterator, Tuple


from gladier.exc import FlowGenException

log = logging.getLogger(__name__)

STATE_TRANSITION_KEYS = {"Next", "Default", "StartAt"}


def get_transition(state):
    for k in STATE_TRANSITION_KEYS:
        if k in state:
            return k, state[k]


def iter_flow_states(
    flow_states: Mapping[str, Any],
    state: str,
    previously_visited: List[str] = None,
) -> Iterator[Tuple[str, Mapping[str, Any]]]:
    """Iter a Depth first search through a given dict of flow states. Previously
    visited states are skipped."""
    visited = previously_visited.copy() if previously_visited else list()

    if state is None or state in visited:
        return
    visited.append(state)

    if state not in flow_states:
        raise FlowGenException(f'State {state} not in definition!')

    yield state, flow_states[state]

    transition_state = get_transition(flow_states[state])
    if transition_state:
        _, state_name = transition_state
        yield from iter_flow_states(flow_states, state_name, previously_visited=visited)

    state_info = flow_states[state]
    if state_info['Type'] == 'Choice':
        for choice in state_info.get('Choices', []):
            if choice.get('Next'):
                yield from iter_flow_states(flow_states, choice['Next'], previously_visited=visited)
    return


def iter_flow(flow_definition: Mapping[str, Any]) -> Iterator[Tuple[str, Mapping[str, Any]]]:
    """
    Yields a tuple containing the state name and state info for each state in a flow definition.

    """
    yield from iter_flow_states(flow_definition['States'], flow_definition['StartAt'])


def get_end_states(flow_definition: Mapping[str, Any]) -> Iterator[str]:
    """Get all states for a flow that will cause the flow to exit normally. This includes any
    state which contains "End": True. A termination state is assumed if there is no next
    state to transition."""
    yield from {name for name, state in iter_flow(flow_definition) if not get_transition(state)}
