"""Utility detecting which ASGI server is running the app."""

import enum
import inspect


class ASGIServer(enum.StrEnum):
    """The enum of different ASGI servers."""

    UVICORN = "uvicorn"
    UNKNOWN = "unknown"


def detect_server() -> ASGIServer:
    """Detect which ASGI server is running the app.

    This function detects server running the app by inspecting the calling stack.

    Returns:
        ASGIServer: The ASGI server running the app.

    """

    for x in inspect.stack():
        if "uvicorn" in x.filename:
            return ASGIServer.UVICORN
    return ASGIServer.UNKNOWN
