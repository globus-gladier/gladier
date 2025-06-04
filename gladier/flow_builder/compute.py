import logging
from .flow import FlowBuilder
from gladier.utils.name_generation import (
    get_compute_flow_state_name,
    get_compute_function_name,
    get_upper_camel_case,
)
from gladier.exc import FlowGenException

log = logging.getLogger(__name__)


class ComputeFlowBuilderv2(FlowBuilder):

    VALID_COMPUTE_MODIFIERS = {"endpoint", "payload", "tasks"}

    def generic_set_modifier(
        self, item, mod_name, mod_value, flow_definition_reference: dict
    ):
        functions = [f.__name__ for f in self.tool.compute_functions]

        if not isinstance(mod_value, str):
            if mod_value in self.tool.compute_functions:
                sn = self.get_flow_state_name(mod_value)
                mod_value = self.get_state_result_path(sn)
        elif isinstance(mod_value, str) and not mod_value.startswith("$."):
            if mod_value in functions:
                sn = self.get_flow_state_name(mod_value)
                mod_value = self.get_state_result_path(sn)

        return super().generic_set_modifier(
            item, mod_name, mod_value, flow_definition_reference
        )

    def generate_compute_flow_state(self, compute_function):
        state_name = get_compute_flow_state_name(compute_function)

        return state_name, {
            "Comment": compute_function.__doc__,
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org",
            "ExceptionOnActionFailure": False,
            "Parameters": {
                "tasks": [
                    {
                        "endpoint.$": "$.input.compute_endpoint",
                        "function.$": f"$.input.{get_compute_function_name(compute_function)}",
                        "payload.$": "$.input",
                    }
                ]
            },
            "ResultPath": f"$.{state_name}",
            "WaitTime": 300,
        }

    def get_flow_definition(self) -> dict:
        if not self.tool.compute_functions:
            raise FlowGenException()

        states = dict()
        last_state = None
        for func in self.tool.compute_functions:
            name, state_info = self.generate_compute_flow_state(func)
            states[name] = state_info

            if last_state:
                states[last_state]["Next"] = name
            last_state = name
        states[last_state]["End"] = True

        flow = {
            "StartAt": get_compute_flow_state_name(self.tool.compute_functions[0]),
            "States": states,
            "Comment": f"Flow with states: {', '.join(states.keys())}",
        }
        flow = self.apply_modifiers(flow)
        return flow

    def get_flow_state_name(self, state):
        if not isinstance(state, str):
            name = state.__name__
        else:
            name = state

        return get_upper_camel_case(name)

    def apply_modifiers(self, flow):
        for name, mods in self.modifiers.items():
            log.debug(name)
            state_name = self.get_flow_state_name(name)
            log.debug(state_name)
            flow["States"][state_name] = self.apply_modifier(
                flow["States"][state_name], mods, flow
            )
        return flow

    def apply_modifier(
        self, flow_state: str, state_modifiers: dict, flow_definition_reference: dict
    ):
        for modifier_name, value in state_modifiers.items():
            log.debug(f'Applying modifier "{modifier_name}", value "{value}"')
            # If this is for a compute task
            if modifier_name in self.VALID_COMPUTE_MODIFIERS:
                if modifier_name == "tasks":
                    flow_state["Parameters"] = self.generic_set_modifier(
                        flow_state["Parameters"],
                        "tasks",
                        value,
                        flow_definition_reference,
                    )
                else:
                    flow_state["Parameters"]["tasks"] = [
                        self.generic_set_modifier(
                            fx_task, modifier_name, value, flow_definition_reference
                        )
                        for fx_task in flow_state["Parameters"]["tasks"]
                    ]
            elif modifier_name in self.VALID_STATE_MODIFIERS:
                self.generic_set_modifier(
                    flow_state, modifier_name, value, flow_definition_reference
                )
        return flow_state


class ComputeFlowBuilderv3(FlowBuilder):
    def generate_compute_flow_state(compute_function):
        state_name = get_compute_flow_state_name(compute_function)

        return state_name, {
            "Comment": compute_function.__doc__,
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org/v3",
            "ExceptionOnActionFailure": True,
            "Parameters": {
                "endpoint_id.$": "$.input.compute_endpoint",
                "tasks": [
                    {
                        "function_id.$": f"$.input.{get_compute_function_name(compute_function)}",
                        "kwargs.$": "$.input",
                    }
                ],
            },
            "ResultPath": f"$.{state_name}",
            "WaitTime": 300,
        }
