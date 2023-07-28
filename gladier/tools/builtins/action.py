import typing as t
from collections import defaultdict
from enum import Enum

from gladier import (
    AWSBaseState,
    JSONObject,
    StateWithNextOrEnd,
    StateWithParametersOrInputPath,
    StateWithResultPath,
)
from gladier.helpers import eliminate_none_values


class ActionExceptionName(str, Enum):
    """
    Names of all possible exceptions that can be thrown by Globus Action Provider states.
    """

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
    """The Action State defines the base class for all Globus Action Providers."""

    action_url: str
    state_type: str = "Action"
    action_scope: t.Optional[str] = None
    wait_time: int = 600
    input_path: t.Optional[str] = None
    exception_on_action_failure: bool = False
    run_as: t.Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception_handlers: t.Dict[ActionExceptionName, AWSBaseState] = {}

    def set_exception_handler(
        self,
        exception_names: t.Union[ActionExceptionName, t.List[ActionExceptionName]],
        exception_handler: AWSBaseState,
    ):
        """
        Set an exception handler in case any state raises an exception during a flow.

        :param exception_names: Can be a string of one exception name or a list of any defined within
        the ActionExceptionName Class.
        :param exception_handler: Name of the state which will be run if any of the ``exception_names`` above
        are encountered.
        """
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

    def get_child_states(self) -> t.List[AWSBaseState]:
        next_states = super().get_child_states()
        exception_handler_states = list(self.exception_handlers.values())
        return next_states + exception_handler_states
