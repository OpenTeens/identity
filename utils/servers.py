import enum
import inspect


class ASGIServer(enum.StrEnum):
    UVICORN = "uvicorn"
    UNKNOWN = "unknown"


def detect_server() -> ASGIServer:
    for x in inspect.stack():
        if "uvicorn" in x.filename:
            return ASGIServer.UVICORN
    return ASGIServer.UNKNOWN
