from __future__ import annotations

import typing as t

from .builtins import (
    ActionState,
    AndRule,
    ChoiceOption,
    ChoiceRule,
    ChoiceState,
    ComparisonRule,
    ExpressionEvalState,
    FailState,
    NotRule,
    OrRule,
    PassState,
    WaitState,
)
from .globus import (
    Compute,
    ComputeFunctionType,
    SearchDelete,
    SearchDeleteByQuery,
    SearchIngest,
    Transfer,
    TransferDelete,
    TransferItem,
)
from .helpers import exclusive_validator_generator, validate_path_property

_nameables = (
    x.__name__
    for x in (
        ActionState,
        AndRule,
        ChoiceOption,
        ChoiceRule,
        ChoiceState,
        ComparisonRule,
        ExpressionEvalState,
        FailState,
        NotRule,
        OrRule,
        PassState,
        WaitState,
        Compute,
        ComputeFunctionType,
        SearchDelete,
        SearchDeleteByQuery,
        SearchIngest,
        Transfer,
        TransferDelete,
        TransferItem,
        exclusive_validator_generator,
        validate_path_property,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = []

__all__ = tuple(_nameables) + tuple(_unnameables)
