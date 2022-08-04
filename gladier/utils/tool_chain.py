import logging
import json
import copy
from collections import OrderedDict

from gladier.exc import FlowGenException, StateNameConflict

log = logging.getLogger(__name__)


class ToolChain:

    def __init__(self, tools, flow_comment=None):
        self.tools = tools
        self.states = dict()
        self._flow_definition = None
        self.flow_comment = flow_comment

    @property
    def flow_definition(self):
        return json.loads(json.dumps(self._flow_definition))

    @property
    def ordered_flow_definition(self):
        return self._flow_definition

    def compile_flow(self):
        self.check_tools()
        self.states = OrderedDict()
        for tool in self.tools:
            new_states = self.get_unique_states(tool)
            log.debug(f'Adding tool {tool} to flow...')
            if set(new_states.keys()).intersection(set(self.states.keys())):
                raise StateNameConflict(f'Tool {tool} has a conflicting state name.')
            self.states.update(new_states)
        self._flow_definition = self.combine_flow_states(self.states, self.flow_comment)

    def get_unique_states(self, tool):
        unique_flow_states = OrderedDict()
        for state_name, state_data in self.get_ordered_flow_states(tool.flow_definition).items():
            if tool.alias:
                log.debug(f'Renaming state {state_name} to use alias {tool.alias}')
                state_name, state_data = tool.rename_state(state_name, state_data)
            unique_flow_states[state_name] = state_data
        log.debug(f'Complete flow states: {list(unique_flow_states.keys())}')
        return unique_flow_states

    def check_tools(self):
        for tool in self.tools:
            if tool.flow_definition is None:
                raise FlowGenException(f'Tool {tool} did not set .flow_definition attribute or set '
                                       f'@generate_flow_definition (funcx functions only). Please '
                                       f'set a flow definition for {tool.__class__.__name__}.')

    @staticmethod
    def combine_flow_states(flow_states, flow_comment=None):
        """
        Given a GlaiderBaseClient or GladierBaseTool, generate a complete automate flow.
        """
        keylist = list(flow_states.keys())
        first, last = keylist[0], keylist[-1]
        flow_definition = OrderedDict([
            ('Comment', flow_comment),
            ('StartAt', first),
            ('States', flow_states)
        ])

        for fs_data in flow_states.values():
            if fs_data.get('End'):
                fs_data.pop('End')

        # Set the order for each of the flow states. Order is linear, based
        # on the order of the funcx functions defined in the tool
        for state_name, state_data in flow_states.items():
            if state_name == last:
                state_data['End'] = True
            else:
                next_index = keylist.index(state_name) + 1
                state_data['Next'] = keylist[next_index]
        if not flow_definition['Comment']:
            state_names = ", ".join(flow_definition["States"].keys())
            flow_definition['Comment'] = f'Flow with states: {state_names}'

        return flow_definition

    @staticmethod
    def get_ordered_flow_states(flow_definition):
        flow_def = copy.deepcopy(flow_definition)
        ordered_states = OrderedDict()
        state = flow_def['StartAt']
        while state is not None:
            ordered_states[state] = flow_def['States'][state]
            if flow_def['States'][state].get('Next'):
                state = flow_def['States'][state].get('Next')
            elif flow_def['States'][state].get('End') is True:
                break
            else:
                raise FlowGenException(f'Flow definition has no "Next" or "End" for state '
                                       f'"{state}" with states: {flow_def["States"].keys()}')

        ordered_states[state] = flow_def['States'][state]
        return ordered_states
