from __future__ import annotations

import typing as t

from .compute import GlobusComputeStep, ComputeFunctionType
from .transfer import GlobusTransfer, GlobusTransferItem

_nameables = (
    x.__name__
    for x in (GlobusComputeStep, GlobusTransfer, GlobusTransferItem)
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = ["ComputeFunctionType"]

__all__ = tuple(_nameables) + tuple(_unnameables)
