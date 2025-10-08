import logging
import typing as t
from gladier.exc import FlowModifierException, FlowGenException

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
            "ResultPath": f"$.{self.get_default_flow_state_name()}",
            "WaitTime": self.wait_time,
        }

    def get_flow_definition(self) -> dict:
        return {
            "StartAt": self.get_default_flow_state_name(),
            "States": {self.get_default_flow_state_name(): self.get_state_definition()},
        }

    def get_applicable_modifiers(self, modifiers, matching_only=False):
        """
        Get modifiers that apply to this tool. Raise an exception if matching_only is true and modifiers do not
        apply to this tool.
        """
        applicable_modifiers = {}
        state_names = self.get_flow_state_names()
        for modifier_name, modifier_data in modifiers.items():
            modifier_state_name = self.get_state_name_from_modifier_name(modifier_name)
            if modifier_state_name in state_names:
                self.check_modifier(modifier_name, modifier_data)
                applicable_modifiers[modifier_state_name] = modifier_data

            else:
                log.debug(
                    f"Rejected {modifier_state_name} ({modifier_name}) from Tool {self}"
                )
                if matching_only is False:
                    raise FlowModifierException(f"Invalid Modifier {modifier_name}")
        return applicable_modifiers

        modifier_names = [
            self.get_state_name_from_modifier_name(m) for m in modifiers.keys()
        ]
        applicable_modifier_names = set(modifier_names).intersection(
            set(self.get_flow_state_names())
        )
        log.debug(
            f"Applicable Modifier Names for {self} with states ({self.get_flow_state_names()}): {applicable_modifier_names}"
        )
        return {
            name: mdata
            for name, mdata in modifiers.items()
            if name in applicable_modifier_names
        }

    def apply_modifiers(self, modifiers: dict, flow: dict, matching_only: bool = False):
        """
        Apply modifiers to the given flow. The flow is passed in externally, presumably by a separate entity building the
        code. ``matching_only`` will determine whether an exception is raised if modifiers passed in don't match the flow
        states on the flow, which can happen usually if flow evaluation is happening for all the states, where each tool is
        evaluated individually and modifiers that don't apply to a particular tool are skipped.

        :param modifiers: A dict of modifiers. {func/state: {flow_key_val.$: $.flow_value}}
        :param matching_only: if True, raise an exception if modifiers don't match up.

        """
        if not isinstance(modifiers, dict):
            raise FlowGenException("Modifiers must be a dict keyed by flow step name")

        # Hmm, only want to check this against the current list of possible modifiers in the flow managed by this flow builder.
        applicable_modifiers = self.get_applicable_modifiers(
            modifiers, matching_only=matching_only
        )
        log.debug(
            f"Applying Modifiers {modifiers.keys()} for tool {self}, matching_only={matching_only}, applied={applicable_modifiers.keys()}"
        )

        for name, mods in applicable_modifiers.items():
            state_name = self.get_state_name_from_modifier_name(name)
            flow["States"][state_name] = self.apply_modifier(
                flow["States"][state_name], mods, flow
            )
        return flow

    def get_state_name_from_modifier_name(self, modifier_name) -> str:
        """This should probably change in the future. Gladier allows you to pass in a few different types of names as modifiers
        for a given state. The modifier_name *may* be a string, but it could also be a function. This should be overridden
        to account for any allowed custom names."""
        return modifier_name

    def get_flow_state_names(self) -> t.List[str]:
        return list(self.get_flow_definition()["States"].keys())

    def get_default_flow_state_name(self) -> str:
        """
        Get the typical flow state name that should be expected by this tool.
        """
        return self.tool.__class__.__name__

    def get_state_result_path(self, state=None):
        state = state or self.get_flow_state_name()
        return f"$.{state}.details.results"

    def get_valid_modifier_names(self):
        return self.VALID_STATE_MODIFIERS

    def check_modifier(self, modifer_name: str, modifier_data: dict):
        for mod_name in modifier_data.keys():
            if mod_name not in self.get_valid_modifier_names():
                raise FlowModifierException(
                    f"Class {self.tool}: Unsupported modifier "
                    f'"{modifer_name}". The only supported modifiers are: '
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
