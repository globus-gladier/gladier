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
    insure_parameter_values,
)


class GladierBaseState(ABC, BaseModel):
    state_type: str
    state_name: t.Optional[str] = None
    comment: t.Optional[str] = None

    class Config:
        extra = Extra.allow

    @property
    def valid_state_name(self) -> str:
        return self.state_name or type(self).__name__

    @abstractmethod
    def get_flow_definition(self) -> JSONObject:
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
        try:
            flow_def = self._flow_definition
        except AttributeError:
            flow_def = self.get_flow_definition()
        return flow_def.get("States", {}).get(self.valid_state_name)

    def add_state_to_flow_definition(self, other_state: GladierBaseState) -> JSONObject:
        flow_def = GladierBaseState.get_flow_definition(self)
        if other_state.valid_state_name not in flow_def["States"]:
            # other_state.get_flow_definition() # Force full generation of the state
            flow_def["States"][
                other_state.valid_state_name
            ] = other_state.get_flow_state_dict()
        return self._flow_definition

    def get_additional_scopes_for_input(self, flow_input: JSONObject) -> t.Set[str]:
        return set()

    def get_child_states(self) -> t.List[GladierBaseState]:
        return []

    def get_flow_transition_states(self) -> t.List[str]:
        """
        For compatibility with the tool model flow generation
        """
        return []


class GladierBaseCompositeState(GladierBaseState):
    state_name_prefix: t.Optional[str] = None

    @abstractmethod
    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()


class StateWithNextOrEnd(GladierBaseState):
    def next(self, next_state: GladierBaseState) -> GladierBaseState:
        self.next_state = next_state
        return next_state

    def get_child_states(self) -> t.List[GladierBaseState]:
        super_children = super().get_child_states()
        try:
            super_children.append(self.next_state)
        except AttributeError:
            pass
        return super_children

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        try:
            state_def["Next"] = self.next_state.valid_state_name
        except AttributeError:
            state_def["End"] = True
        return flow_definition


class StateWithParametersOrInputPath(GladierBaseState, ABC):
    parameters: t.Optional[t.Dict[str, t.Any]] = None
    input_path: t.Optional[str] = None

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        params_or_input_path = {}

        if self.parameters is not None:
            if self.input_path is not None:
                raise ValueError(
                    "A state can only have one of 'parameters' and 'input_path'"
                )
            params_or_input_path["Parameters"] = insure_parameter_values(
                self.parameters
            )
        elif self.input_path is not None:
            params_or_input_path["InputPath"] = ensure_json_path(self.input_path)

        flow_state.update(params_or_input_path)
        return flow_definition


class StateWithResultPath(GladierBaseState, ABC):
    result_path: t.Optional[str] = None

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        result_path = (
            self.result_path
            if self.result_path is not None
            else f"$.{self.valid_state_name}Result"
        )
        flow_state.update({"ResultPath": ensure_json_path(result_path)})
        return flow_definition


class ActionExceptionName(str, Enum):
    ActionFailedException = "ActionFailedException"
    ActionUnableToRun = "ActionUnableToRun"
    ActionTimeout = "ActionTimeout"
    NoTokenException = "NoTokenException"
    States_All = "States.All"
    States_IntrinsicFailure = "States.IntrinsicFailure"
    States_ParameterPathFailure = "States.ParameterPathFailure"
    States_ResultPathMatchFailure = "States.ResultPathMatchFailure"


class ActionState(
    StateWithNextOrEnd,
    StateWithParametersOrInputPath,
    StateWithResultPath,
):
    action_url: str
    state_type: str = "Action"
    action_scope: t.Optional[str] = None
    wait_time: int = 600
    input_path: t.Optional[str] = None
    exception_on_action_failure: bool = False
    run_as: t.Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception_handlers: t.Dict[ActionExceptionName, GladierBaseState] = {}

    def set_exception_handler(
        self,
        exception_names: t.Union[ActionExceptionName, t.List[ActionExceptionName]],
        exception_handler: GladierBaseState,
    ):
        if isinstance(exception_names, ActionExceptionName):
            exception_names = [exception_names]
        for exc_name in exception_names:
            self.exception_handlers[exc_name] = exception_handler

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        action_flow_state: JSONObject = {
            "ActionUrl": self.action_url,
            "WaitTime": self.wait_time,
            "ActionScope": self.action_scope,
            "ExceptionOnActionFailure": self.exception_on_action_failure,
        }
        if len(self.exception_handlers) > 0:
            catches: t.Dict[str, t.Set[str]] = defaultdict(set)
            # Create an "inverted" dictionary of the exception name -> handler dictionary
            # tracked on the object so that we have one entry per handler state with the
            # set of exceptions which are handled by that state as values
            for exc_name, handler_state in self.exception_handlers.items():
                catches[handler_state.valid_state_name].add(exc_name.value)
            # Now re-invert to the format for the Catch clause on the state
            action_flow_state["Catch"] = [
                {"ErrorEquals": list(exc_names), "Next": handler}
                for handler, exc_names in catches.items()
            ]
        flow_state.update(action_flow_state)
        eliminate_none_values(flow_state, deep=True)
        return flow_definition

    def get_child_states(self) -> t.List[GladierBaseState]:
        next_states = super().get_child_states()
        exception_handler_states = list(self.exception_handlers.values())
        return next_states + exception_handler_states
