from __future__ import annotations

import typing as t

from .choice_state import (
    AndRule,
    ChoiceOption,
    ChoiceState,
    ComparisonRule,
    NotRule,
    OrRule,
)
from .fail import FailState
from .pass_state import PassState
from .succeed import SucceedState
from .wait import WaitState

_nameables = (
    x.__name__
    for x in (
        AndRule,
        ChoiceOption,
        ChoiceState,
        ComparisonRule,
        NotRule,
        OrRule,
        PassState,
        WaitState,
        FailState,
        SucceedState,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = []

__all__ = tuple(_nameables) + tuple(_unnameables)
