import logging
from typing import Mapping, Any, List
import copy

from gladier.base import GladierBaseTool
from gladier.exc import FlowGenException, StateNameConflict
from gladier.utils.flow_traversal import get_end_states

log = logging.getLogger(__name__)


class ToolChain:

    def __init__(self, flow_comment=None):
        self._flow_definition = {
            'States': dict(),
            'Comment': flow_comment,
            'StartAt': None,
        }
        self.transition_states = list()

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

            flow_definition = tool.get_flow_definition()
            self._chain_flow(flow_definition, self.transition_states)
            # Use the tool-defined states if they are defined, otherwise there is only one
            # End state on the flow and therefore can be assumed.
            t_states = list(get_end_states(flow_definition))
            tool_t_states = tool.get_flow_transition_states()
            if len(t_states) > 1 and not tool_t_states:
                raise FlowGenException(f'Tool {tool} has multiple branching end states and must '
                                       'define which states a flow may continue by setting '
                                       '"flow_transition_states" containing one or more of '
                                       f'{", ".join(t_states)} ')
            elif not t_states:
                raise FlowGenException(f'{tool}: Could not find any end states in flow.')

            self.transition_states = tool_t_states if tool_t_states else t_states
        return self

    def chain_state(self, name: str, definition: Mapping[str, Any]):
        log.debug(f'Chaining state {name} with definition {definition.keys()}')
        temp_flow = {
            'StartAt': name,
            'States': {name: definition},
        }
        temp_flow['States'][name]['End'] = True
        self._chain_flow(temp_flow, [name])
        return self

    def _chain_flow(self, new_flow: Mapping[str, dict], transition_states: List[str]):
        # Base case, if this is the first 'chain' and no states exist yet.
        if not self._flow_definition['States']:
            self._flow_definition['States'] = copy.deepcopy(new_flow['States'])
            self._flow_definition['StartAt'] = new_flow['StartAt']
            return

        self._flow_definition['States'].update(new_flow['States'])
        for t_state in transition_states:
            self.add_transition(t_state, new_flow['StartAt'])

    def add_transition(self, cur_flow_term: str, new_chain_start: str):
        if self._flow_definition['States'][cur_flow_term].get('End'):
            self._flow_definition['States'][cur_flow_term].pop('End')
        log.debug(f'Chaining {cur_flow_term} --> {new_chain_start}')
        self._flow_definition['States'][cur_flow_term]['Next'] = new_chain_start

    def check_tools(self, tools: List[GladierBaseTool]):

        states = set()
        for tool in tools:
            flow_def = tool.get_flow_definition()
            if flow_def is None:
                raise FlowGenException(f'Tool {tool} did not set .flow_definition attribute or set '
                                       f'@generate_flow_definition (funcx functions only). Please '
                                       f'set a flow definition for {tool.__class__.__name__}.')

            new_states = set(flow_def.get('States'))
            conflicts = states & new_states
            if conflicts:
                raise StateNameConflict(f'States in tool {tool} '
                                        f'has been defined more than once: {conflicts}')
            states = states | new_states
