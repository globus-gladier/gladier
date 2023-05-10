from __future__ import annotations

import logging
import typing as t

from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.decorators import generate_flow_definition
from gladier.managers import CallbackLoginManager, FlowsManager

from .helpers import JSONList, JSONObject, JSONValue
from .state_models import (
    GladierActionState,
    GladierBaseState,
    GladierStateWithNextOrEnd,
    GladierStateWithParametersOrInputPath,
    GladierStateWithResultPath,
)

_nameables = (
    x.__name__
    for x in (
        GladierBaseTool,
        GladierBaseClient,
        generate_flow_definition,
        CallbackLoginManager,
        FlowsManager,
        GladierActionState,
        GladierBaseState,
        GladierStateWithNextOrEnd,
        GladierStateWithParametersOrInputPath,
        GladierStateWithResultPath,
    )
    if hasattr(x, "__name__")
)
_unnameables: t.List[str] = ["JSONObject", "JSONList", "JSONValue"]

__all__ = tuple(_nameables) + tuple(_unnameables)


# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library  # noqa
logging.getLogger("gladier").addHandler(logging.NullHandler())
