import logging
from gladier.exc import FlowModifierException

log = logging.getLogger(__name__)


class FlowBuilder:
    """
    TODO: Apply modifiers to a specific tool

    But also, allow applying modifiers given a list of tools.
    """

    type = "Action"
    comment = ""
    action_url = ""
    wait_time = 300
    parameters = "$.input."
    exception_on_action_failure = True
    end = True

    VALID_STATE_MODIFIERS = {
        "Type",
        "ActionUrl",
        "WaitTime",
        "ExceptionOnActionFailure",
        "RunAs",
        "InputPath",
        "Parameters",
        "ResultPath",
        "Catch",
        "ActionScope",
        "Next",
        "End",
    }

    def __init__(self, tool):
        self.tool = tool

    def get_state_definition(self) -> dict:
        return {
            "Comment": self.comment,
            "Type": self.type,
            "ActionUrl": self.action_url,
            "ExceptionOnActionFailure": self.exception_on_action_failure,
            "Parameters": self.parameters,
            "ResultPath": f"$.{self.get_flow_state_name()}",
            "WaitTime": self.wait_time,
        }

    def get_flow_definition(self) -> dict:
        name = self.get_flow_state_name()
        flow = {
            "StartAt": name,
            "States": {
                name: self.get_state_definition(),
            },
        }
        return flow

    def apply_modifiers(self, modifiers, flow, strict: bool = True):
        self.check_modifiers(modifiers)
        for name, mods in modifiers.items():
            state_name = self.get_flow_state_name(name)
            flow["States"][state_name] = self.apply_modifier(
                flow["States"][state_name], mods, flow
            )
        return flow

    def get_flow_state_name(self, state=None):
        return state or self.tool.__class__.__name__

    def get_state_result_path(self, state=None):
        state = state or self.get_flow_state_name()
        return f"$.{state}.details.results"

    def get_function(self, name):
        for f in self.tool.compute_functions:
            if callable(name):
                fname = name.__name__
            else:
                fname = name
            if fname == f.__name__:
                return f

    def get_valid_modifier_names(self):
        return self.VALID_STATE_MODIFIERS

    def check_modifiers(self, modifiers):
        log.debug(f"Checking modifiers: {modifiers}")
        if not isinstance(modifiers, dict):
            raise FlowModifierException(f"{self.tool}: Flow Modifiers must be a dict")

        legacy_funcs = getattr(self.tool, "funcx_functions", [])
        legacy_func_names = [f.__name__ for f in legacy_funcs]

        # Check if modifiers were set correctly
        for name, mods in modifiers.items():
            if name in legacy_func_names:
                raise FlowModifierException(
                    f"Class {self.tool} is a Legacy Gladier tool pre-v0.9.0. Please use a modern "
                    "version or follow the migration guide here to make it compatible: \n\n"
                    "\thttps://gladier.readthedocs.io/en/latest/migration.html\n"
                )

            if not self.get_function(name):
                raise FlowModifierException(
                    f"Class {self.tool} included modifier which does not "
                    f"exist: {name}. Allowed modifiers include "
                    f'{", ".join([f.__name__ for f in self.tool.compute_functions])}'
                )

            for mod_name, mod_value in mods.items():
                if mod_name not in self.get_valid_modifier_names():
                    raise FlowModifierException(
                        f"Class {self.tool}: Unsupported modifier "
                        f'"{mod_name}". The only supported modifiers are: '
                        f"{self.get_valid_modifier_names()}"
                    )

    def generic_set_modifier(
        self, item, mod_name, mod_value, flow_definition_reference: dict
    ):
        if isinstance(mod_value, str) and not mod_value.startswith("$."):
            if mod_value in flow_definition_reference["States"].keys():
                mod_value = self.get_state_result_path(mod_value)
            elif mod_name not in self.VALID_STATE_MODIFIERS:
                mod_value = f"$.input.{mod_value}"

        # Remove duplicate keys
        for duplicate_mod_key in (mod_name, f"{mod_name}.$"):
            if duplicate_mod_key in item.keys():
                item.pop(duplicate_mod_key)

        # Note: Top level State types don't end with '.$', all others must end with
        # '.$' to indicate the value should be replaced. '.=' is not supported or possible yet
        if isinstance(mod_value, str) and mod_value.startswith("$."):
            mod_name = f"{mod_name}.$"
        item[mod_name] = mod_value
        log.debug(f"Set modifier {mod_name} to {mod_value}")
        return item
