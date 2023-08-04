from __future__ import annotations

import typing as t

from .compute import ComputeFunctionType, GlobusComputeState
from .transfer import GlobusTransfer, GlobusTransferDelete, GlobusTransferItem
from .search import SearchIngest, SearchDelete, SearchDeleteByQuery

_nameables = (
    x.__name__
    for x in (
        ComputeFunctionType,
        GlobusComputeState,
        GlobusTransfer,
        GlobusTransferDelete,
        GlobusTransferItem,
        SearchIngest,
        SearchDelete,
        SearchDeleteByQuery,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = ["ComputeFunctionType"]

__all__ = tuple(_nameables) + tuple(_unnameables)
