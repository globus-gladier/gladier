from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum

from pydantic import BaseModel, Extra

from .helpers import (
    JSONObject,
    eliminate_none_values,
    ensure_json_path,
    ensure_parameter_values,
)


class BaseState(ABC, BaseModel):
    """
    Base object to define the basic structure of the State API. The Base state ensures
    that overriding classes will set a get_flow_definition() method and supplies some extra
    hooks for defining more complex behavior around deploying flows, for instance if a
    state could require extra scopes.
    """

    state_type: str
    state_name: t.Optional[str] = None
    comment: t.Optional[str] = None

    class Config:
        extra = Extra.allow

    @property
    def valid_state_name(self) -> str:
        """Return the valid state name of this state, either explicitly passed in by the user
        or automatically generated by the name of the overriding class."""
        return self.state_name or type(self).__name__

    @abstractmethod
    def get_flow_definition(self) -> JSONObject:
        """This is the base abstract implementation for get_flow_definition, which ensures the basic
        properties of a flow definition which MUST be in place and will build a complete flow definition
        for any child states which are set."""
        try:
            return self._flow_definition
        except AttributeError:
            pass
        flow: JSONObject = {
            "StartAt": self.valid_state_name,
            "States": {self.valid_state_name: {"Type": self.state_type}},
        }
        flow["Comment"] = (
            self.comment
            if self.comment is not None
            else f"Flow starting at state {self.valid_state_name}"
        )

        # Now, add all the children into our flow
        # TODO: This will recurse forever if there is a loop in the flow
        #   but, so will pydantic printing or serializing any state, so this
        #   probably needs to be thought about at a higher level.
        for child_state in self.get_child_states():
            if child_state.valid_state_name not in flow["States"]:
                child_flow = child_state.get_flow_definition()
                for child_flow_state_name, child_flow_state_def in child_flow[
                    "States"
                ].items():
                    if child_flow_state_name not in flow["States"]:
                        flow["States"][child_flow_state_name] = child_flow_state_def
        self._flow_definition = flow
        return flow

    def get_flow_state_dict(self) -> JSONObject:
        """
        Get a flow definition for this state, which can either be get_flow_definition() if the flow
        has not yet been built, or the _flow_definition attribute if this has been called before.
        """
        try:
            flow_def = self._flow_definition
        except AttributeError:
            flow_def = self.get_flow_definition()
        return flow_def.get("States", {}).get(self.valid_state_name)

    def get_additional_scopes_for_input(self, flow_input: JSONObject) -> t.Set[str]:
        """
        Additional hook in case the input causes other required dependent scopes as part of the flow.
        Currently, this is only used in the case of a Mapped Collection data_access scope, where the
        collection passed in as input requires this scope at run_flow time in order for the running flow
        to complete successfully, or else the flow will fail.
        """
        return set()

    def get_child_states(self) -> t.List[BaseState]:
        """
        Get any cached child states present on this state which have previously been added
        """
        return []

    def get_flow_transition_states(self) -> t.List[str]:
        """
        For compatibility with the tool model flow generation
        """
        return []


class BaseCompositeState(BaseState):
    """
    A class which allows combining two or more base states
    """

    state_type: str = "CompositeVirtualState"
    state_name_prefix: str = ""

    @abstractmethod
    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()


class StateWithNextOrEnd(BaseState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_state: t.Optional[BaseState] = None

    def next(
        self,
        next_state: BaseState,
        insert_next: bool = False,
        replace_next: bool = False,
    ) -> BaseState:
        """Set another state as the Next for this state

        Set the provided next_state as the next state in the Flow after the Flow rooting
        at this state. That is, the provided next_state will become the new "last" state
        in the Flow starting with this state. This allows for chaining multiple calls to
        the method with each adding to the end of the Flow. The options insert and
        replace change this behavior as described.

        Args:
            next_state: The state to set as Next after this state in the Flow.
            insert_next: If True, insert the next_state immediately after this state,
                retaining the rest of the flow currently referred to as next after the
                inserted state.
            replace_next: If True, remove all states in the Flow after this state and
                replace it with the provided next_state

        Returns:
            the state next is invoked upon allowing for chaining of calls to next
        """

        new_next_state: t.Optional[BaseState] = next_state
        if replace_next:
            self.next_state = next_state
            return self
        if insert_next:
            old_next = self.next_state
            self.next_state = next_state
            new_next_state = old_next
        if self.next_state is None:
            self.next_state = new_next_state
        elif (
            isinstance(self.next_state, StateWithNextOrEnd)
            and new_next_state is not None
        ):
            self.next_state.next(new_next_state)
        return self

    def get_child_states(self) -> t.List[BaseState]:
        """
        Get child states.

        TODO: It isn't clear to me why this may be raising attribute errors.
        """
        super_children = super().get_child_states()
        if self.next_state is not None:
            super_children.append(self.next_state)
        return super_children

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        if self.next_state is not None:
            state_def["Next"] = self.next_state.valid_state_name
        else:
            state_def["End"] = True
        return flow_definition


_common_non_parameter_properties = set(
    [
        "state_type",
        "set_parameters_from_properties",
        "non_parameter_properties",
        "action_url",
        "wait_time",
        "exception_on_action_failure",
        "exception_handlers",
        "_flow_definition",
        "action_scope",
        "comment",
        "input_path",
        "parameters",
        "result_path",
        "run_as",
        "state_name",
        "next_state",
    ]
)


class StateWithParametersOrInputPath(BaseState, ABC):
    """
    Mixin class to enforce either parameters or input tpaths on a given states
    flow definition. A state with this inherited class may ONLY have
    parameters or input_path, or a ValueError is raised.
    """

    parameters: t.Optional[t.Dict[str, t.Any]] = None
    input_path: t.Optional[str] = None
    set_parameters_from_properties: bool = True
    non_parameter_properties: t.Set[str] = _common_non_parameter_properties

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        params_or_input_path: JSONObject = {}

        # Presence of input_path takes precedence over parameter values because parameter
        # values are likely to be present from model defaults even if not explicitly set
        # (or desired) by the user
        if self.input_path is not None:
            params_or_input_path["InputPath"] = ensure_json_path(self.input_path)
        else:
            if self.parameters is None and self.set_parameters_from_properties:
                self.parameters = self.dict()
                for prop_name in self.non_parameter_properties:
                    self.parameters.pop(prop_name, None)

            if self.parameters is not None and len(self.parameters) > 0:
                params_or_input_path["Parameters"] = ensure_parameter_values(
                    self.parameters
                )

        flow_state.update(params_or_input_path)
        return flow_definition


class StateWithResultPath(BaseState, ABC):
    """
    Mixin to ensure a given state has a ResultPath associated with it. By
    default, the result path will be generated from the name of the state, but
    may also be overridden with the result_path parameter.

    """

    result_path: t.Optional[str] = None

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        flow_state.update({"ResultPath": self.result_path_for_step()})
        return flow_definition

    def result_path_for_step(self) -> str:
        result_path = (
            self.result_path
            if self.result_path is not None
            else f"$.{self.valid_state_name}Result"
        )
        result_path = ensure_json_path(result_path)
        return result_path
