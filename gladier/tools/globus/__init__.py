from __future__ import annotations

import typing as t

from .compute import ComputeFunctionType, Compute
from .transfer import Transfer, TransferDelete, TransferItem
from .search import SearchIngest, SearchDelete, SearchDeleteByQuery

_nameables = (
    x.__name__
    for x in (
        ComputeFunctionType,
        Compute,
        Transfer,
        TransferDelete,
        TransferItem,
        SearchIngest,
        SearchDelete,
        SearchDeleteByQuery,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = ["ComputeFunctionType"]

__all__ = tuple(_nameables) + tuple(_unnameables)
