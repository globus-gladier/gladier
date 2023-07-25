from __future__ import annotations

import typing as t

from .compute import ComputeFunctionType, GlobusComputeState
from .transfer import GlobusTransfer, GlobusTransferDelete, GlobusTransferItem

_nameables = (
    x.__name__
    for x in (
        GlobusComputeState,
        GlobusTransfer,
        GlobusTransferDelete,
        GlobusTransferItem,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = ["ComputeFunctionType"]

__all__ = tuple(_nameables) + tuple(_unnameables)
