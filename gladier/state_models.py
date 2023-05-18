from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

from pydantic import BaseModel, Extra

from .helpers import (
    JSONObject,
    eliminate_none_values,
    insure_json_path,
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


class GladierBaseCompositeState(GladierBaseState):
    state_name_prefix: t.Optional[str] = None

    @abstractmethod
    def get_flow_definition(self) -> JSONObject:
        return super().get_flow_definition()


class GladierStateWithNextOrEnd(GladierBaseState):
    def next(self, next_state: GladierBaseState) -> GladierBaseState:
        self.next_state = next_state
        return next_state

    def get_child_states(self) -> t.List[GladierBaseState]:
        try:
            return [
                self.next_state,
            ]
        except AttributeError:
            return []

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        state_def = self.get_flow_state_dict()
        try:
            state_def["Next"] = self.next_state.valid_state_name
            self.add_state_to_flow_definition(self.next_state)
        except AttributeError:
            state_def["End"] = True
        return flow_definition


class GladierStateWithParametersOrInputPath(GladierBaseState, ABC):
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
            params_or_input_path["InputPath"] = insure_json_path(self.input_path)

        flow_state.update(params_or_input_path)
        return flow_definition


class GladierStateWithResultPath(GladierBaseState, ABC):
    result_path: t.Optional[str] = None

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        result_path = (
            self.result_path
            if self.result_path is not None
            else f"$.{self.valid_state_name}Result"
        )
        flow_state.update({"ResultPath": insure_json_path(result_path)})
        return flow_definition




class GladierActionState(
    GladierStateWithNextOrEnd,
    GladierStateWithParametersOrInputPath,
    GladierStateWithResultPath,
):
    action_url: str
    state_type: str = "Action"
    action_scope: t.Optional[str] = None
    wait_time: int = 600
    input_path: t.Optional[str] = None
    exception_on_action_failure: bool = False
    run_as: t.Optional[str] = None

    def add_exception_handler(
        self, exception_name: str, exception_handler: GladierBaseState
    ):
        ...

    def get_flow_definition(self) -> JSONObject:
        flow_definition = super().get_flow_definition()
        flow_state = self.get_flow_state_dict()
        action_flow_state: JSONObject = {
            "ActionUrl": self.action_url,
            "WaitTime": self.wait_time,
            "ActionScope": self.action_scope,
            "ExceptionOnActionFailure": self.exception_on_action_failure,
        }
        flow_state.update(action_flow_state)
        eliminate_none_values(flow_state, deep=True)
        return flow_definition

    def get_child_states(self) -> t.List[GladierBaseState]:
        next_states = super().get_child_states()
        exception_handler_states: t.List[GladierBaseState] = []  # TODO: Compute this
        return next_states + exception_handler_states
