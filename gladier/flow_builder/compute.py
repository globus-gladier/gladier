import logging
from .flow import FlowBuilder
from gladier.utils.name_generation import (
    get_compute_flow_state_name,
    get_compute_function_name,
    get_upper_camel_case,
)
from gladier.exc import FlowGenException, FlowModifierException

log = logging.getLogger(__name__)


class ComputeFlowBuilderv2(FlowBuilder):

    VALID_COMPUTE_MODIFIERS = {"endpoint", "payload", "tasks"}

    def get_valid_modifier_names(self):
        mods = super().get_valid_modifier_names()
        return mods.union(self.VALID_COMPUTE_MODIFIERS)

    def check_modifier(self, modifier_name: str, modifier_data: dict):
        super().check_modifier(modifier_name, modifier_data)

        legacy_funcs = getattr(self.tool, "funcx_functions", [])
        legacy_func_names = [f.__name__ for f in legacy_funcs]

        if modifier_name in legacy_func_names:
            raise FlowModifierException(
                f"Class {self.tool} is a Legacy Gladier tool pre-v0.9.0. Please use a modern "
                "version or follow the migration guide here to make it compatible: \n\n"
                "\thttps://gladier.readthedocs.io/en/latest/migration.html\n"
            )

    def generic_set_modifier(
        self, item, mod_name, mod_value, flow_definition_reference: dict
    ):
        functions = [f.__name__ for f in self.tool.compute_functions]

        if not isinstance(mod_value, str):
            if mod_value in self.tool.compute_functions:
                sn = self.get_state_name_from_modifier_name(mod_value)
                mod_value = self.get_state_result_path(sn)
        elif isinstance(mod_value, str) and not mod_value.startswith("$."):
            if mod_value in functions:
                sn = self.get_state_name_from_modifier_name(mod_value)
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
        return flow

    def get_state_name_from_modifier_name(self, modifier_name) -> str:
        if not isinstance(modifier_name, str):
            name = modifier_name.__name__
        else:
            name = modifier_name

        name = get_upper_camel_case(name)
        # assert name in self.get_flow_state_names(), f"Modifier name {name} not in {self.get_flow_state_names()}"
        return name

    def get_function(self, name):
        for f in self.tool.compute_functions:
            if callable(name):
                fname = name.__name__
            else:
                fname = name
            if fname == f.__name__:
                return f

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


class ComputeFlowBuilderv3(ComputeFlowBuilderv2):
    """

    https://globus-compute.readthedocs.io/en/latest/actionprovider.html
    """

    VALID_COMPUTE_MODIFIERS = {
        "endpoint_id",
        "tasks",
        "task_group_id",
        "user_endpoint_config",
        "resource_specification",
        "create_queue",
    }

    def apply_modifier(
        self, flow_state: str, state_modifiers: dict, flow_definition_reference: dict
    ):
        for modifier_name, value in state_modifiers.items():
            log.debug(
                f'Applying modifier "{modifier_name}" on v3 compute state, value "{value}"'
            )
            # If this is for a compute task
            if modifier_name in self.VALID_COMPUTE_MODIFIERS:
                flow_state["Parameters"] = self.generic_set_modifier(
                    flow_state["Parameters"],
                    modifier_name,
                    value,
                    flow_definition_reference,
                )
            elif modifier_name in self.VALID_STATE_MODIFIERS:
                self.generic_set_modifier(
                    flow_state, modifier_name, value, flow_definition_reference
                )
        return flow_state

    def generate_compute_flow_state(self, compute_function):
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
