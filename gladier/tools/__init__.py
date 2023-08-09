from __future__ import annotations

import typing as t

from .helpers import exclusive_validator_generator, validate_path_property
from .builtins import ChoiceState, ExpressionEvalState, FailState, WaitState, PassState
from .globus import (
    Compute,
    Transfer,
    TransferItem,
    TransferDelete,
    SearchIngest,
    SearchDelete,
    SearchDeleteByQuery,
)

_nameables = (
    x.__name__
    for x in (
        exclusive_validator_generator,
        validate_path_property,
        ChoiceState,
        ExpressionEvalState,
        FailState,
        WaitState,
        PassState,
        Compute,
        TransferItem,
        Transfer,
        TransferDelete,
        SearchIngest,
        SearchDelete,
        SearchDeleteByQuery,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = []

__all__ = tuple(_nameables) + tuple(_unnameables)
