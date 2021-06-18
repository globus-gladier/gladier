import re
import json
import copy
from collections import OrderedDict

from gladier.exc import FlowGenException


class FlowCompiler:

    def __init__(self, flows, flow_comment=None):
        self.flows = flows
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
        self.states = {}
        for flow in self.flows:
            new_states = self.get_ordered_flow_states(flow)
            new_states = self.get_unique_states(new_states)
            self.states.update(new_states)
        self._flow_definition = self.combine_flow_states(self.states, self.flow_comment)

    def get_incremented_name(self, name):
        m = re.search(r'([a-zA-Z]+)(\d+)$', name)
        if m:
            bare_name, number = m.groups()
            number = int(number)
        else:
            bare_name = name
            number = 1
        number += 1
        return f'{bare_name}{number}'

    def get_unique_state_name(self, name):
        new_name = name
        while new_name in self.states.keys():
            new_name = self.get_incremented_name(new_name)
        return new_name

    def get_unique_states(self, flow_states):
        unique_flow_states = OrderedDict()
        for k, v in flow_states.items():
            unique_flow_states[self.get_unique_state_name(k)] = v
        return unique_flow_states

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
