import typing as t

from gladier import (
    StateWithNextOrEnd,
    StateWithResultPath,
    StateWithParametersOrInputPath,
)


class ExpressionEvalState(
    StateWithParametersOrInputPath, StateWithResultPath, StateWithNextOrEnd
):
    """
    A special Globus Flows state for evaluating expressions within a flow. Examples:


    .. code-block:: JSON

        {
            "expression": "x + 5",
            "arguments": {
                "x": 6
            },
            "result_path": "$.sum_value.should_be_11"
        }

    See more documentation below
    https://docs.globus.org/api/flows/hosted-action-providers/ap-expression-eval/
    """

    parameters: t.Optional[t.Dict[str, t.Any]]
    state_type = "ExpressionEval"
