import typing as t

from gladier import (
    StateWithNextOrEnd,
    StateWithResultPath,
    StateWithParametersOrInputPath,
)


class ExpressionEvalState(
    StateWithParametersOrInputPath, StateWithResultPath, StateWithNextOrEnd
):
    parameters: t.Optional[t.Dict[str, t.Any]]
    state_type = "ExpressionEval"
