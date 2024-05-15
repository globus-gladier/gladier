"""Pydantic V2 provides access to the V1 API, enabling us to
continue using V1 while also supporting V2.

Pattern taken from globus-sdk-common to support both v1 and v2 natively
"""

try:
    from pydantic.v1 import *  # noqa: F401 F403
except ImportError:
    from pydantic import *  # noqa: F401 F403
    from pydantic import *  # type: ignore # noqa: F401 F403
