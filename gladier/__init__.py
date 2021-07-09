import logging
import sys
from gladier.client import GladierBaseClient
from gladier.base import GladierBaseTool
from gladier.decorators import generate_flow_definition

__all__ = [GladierBaseClient, GladierBaseTool, generate_flow_definition]

# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library  # noqa
logging.getLogger("gladier").addHandler(logging.NullHandler())

# This warning can be removed after: https://github.com/funcx-faas/funcX/pull/507
try:
    import funcx_endpoint
    vinfo = sys.version_info
    if vinfo.major == 3 and vinfo.minor > 7 and sys.platform in ['darwin']:
        print('Recommend users downgrade to python 3.7 when using funcx-endpoint.')
except ImportError:
    pass
