import enum  # noqa: D100
import inspect


class ASGIServer(enum.StrEnum):  # noqa: D101
    UVICORN = "uvicorn"
    UNKNOWN = "unknown"


def detect_server() -> ASGIServer:  # noqa: D103
    for x in inspect.stack():
        if "uvicorn" in x.filename:
            return ASGIServer.UVICORN
    return ASGIServer.UNKNOWN
