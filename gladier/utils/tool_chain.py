import logging
from typing import Mapping, Any, List
import copy

from gladier.base import GladierBaseTool
from gladier.exc import FlowGenException

log = logging.getLogger(__name__)


class ToolChain:

    STATE_TRANSITION_KEYS = {"Next", "Default", "StartAt"}

    def __init__(self, flow_comment=None):
        self._flow_definition = {
            'States': [],
            'Comment': flow_comment,
            'StartAt': None,
        }

    @property
    def flow_definition(self):
        flow_def = copy.deepcopy(self._flow_definition)
        if not self._flow_definition.get('Comment'):
            state_names = ", ".join(flow_def["States"].keys())
            flow_def['Comment'] = f'Flow with states: {state_names}'
            return flow_def
        return flow_def

    def chain(self, tools: List[GladierBaseTool]):
        self.check_tools(tools)
        for tool in tools:
            log.debug(f'Chaining tool {tool.__class__.__name__} to existing flow '
                      f'({len(self._flow_definition["States"])} states)')
            self._chain_flow(tool.flow_definition)
        return self

    def chain_state(self, name: str, definition: Mapping[str, Any]):
        log.debug(f'Chaining state {name} with definition {definition.keys()}')
        temp_flow = {
            'StartAt': name,
            'States': {name: definition},
        }
        temp_flow['States'][name]['End'] = True
        self._chain_flow(temp_flow)
        return self

    def _chain_flow(self, new_flow):
        if not self._flow_definition['States']:
            self._flow_definition['States'] = copy.deepcopy(new_flow['States'])
            self._flow_definition['StartAt'] = new_flow['StartAt']
            return

        current_terms = self.get_end_states(self._flow_definition['States'],
                                            self._flow_definition['StartAt'])
        if not current_terms:
            raise FlowGenException(f'Could not find a transition state to '
                                   f'chain flow {self._flow_definition}')

        self._flow_definition['States'].update(new_flow['States'])
        log.debug(f'Chaning main flow {self._flow_definition["StartAt"]}'
                  f'to new flow at {current_terms[0]}')
        self.add_transition(current_terms[0], new_flow['StartAt'])

    def add_transition(self, cur_flow_term: str, new_chain_start: str):
        self._flow_definition['States'][cur_flow_term].pop('End')
        log.debug(f'Chaining {cur_flow_term} --> {new_chain_start}')
        self._flow_definition['States'][cur_flow_term]['Next'] = new_chain_start

    @classmethod
    def _get_transition(cls, state):
        for k in cls.STATE_TRANSITION_KEYS:
            if k in state:
                return k, state[k]

    @classmethod
    def get_end_states(
        cls,
        flow_states: Mapping[str, Any],
        state: str,
        previously_visited: List[str] = None,
    ) -> List[str]:
        end_states = list()
        visited = previously_visited.copy() if previously_visited else list()

        if state is None or state in visited:
            return end_states

        visited.append(state)

        if state not in flow_states:
            raise FlowGenException(f'State {state} not in definition!')

        transition_state = cls._get_transition(flow_states[state])
        if transition_state:
            _, state_name = transition_state
            end_states += cls.get_end_states(flow_states, state_name, previously_visited=visited)
        else:
            if not flow_states[state].get('End'):
                flow_states[state]['End'] = True
            end_states.append(state)

        state_info = flow_states[state]
        if state_info['Type'] == 'Choice':
            for choice in state_info.get('Choices', []):
                if choice.get('Next'):
                    end_states += cls.get_end_states(flow_states, choice['Next'],
                                                     previously_visited=visited)
                elif choice.get('End'):
                    end_states.append(state)
                else:
                    raise FlowGenException(f'Choice state {state} contains invalid choince.')

        return end_states

    def check_tools(self, tools: List[GladierBaseTool]):
        for tool in tools:
            if tool.flow_definition is None:
                raise FlowGenException(f'Tool {tool} did not set .flow_definition attribute or set '
                                       f'@generate_flow_definition (funcx functions only). Please '
                                       f'set a flow definition for {tool.__class__.__name__}.')
        # TODO: Check for state name conflict
