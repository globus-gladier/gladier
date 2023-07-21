from __future__ import annotations

import typing as t

from .compute import GlobusComputeStep, ComputeFunctionType

_nameables = (x.__name__ for x in (GlobusComputeStep,) if hasattr(x, "__name__"))
_unnameables: t.List[str] = ["ComputeFunctionType"]

__all__ = tuple(_nameables) + tuple(_unnameables)
