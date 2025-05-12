import settings
from app.instance import ASGIServer, MyHandler, identity_app_settings, logger, logging
from app.instance import app as app
from utils.servers import detect_server

webserver = detect_server()

if webserver == ASGIServer.UVICORN:
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.handlers = uvicorn_access_logger.handlers = []
    uvicorn_logger.propagate = uvicorn_access_logger.propagate = True


logging.basicConfig(
    level=logging.INFO,
    datefmt="[%x %X]",
    format="{message}",
    style="{",
    handlers=[MyHandler()],
)

if not identity_app_settings.is_prod:
    logger.warning("App is running in development mode.")
    logger.warning("Change it to production mode in production.")

if identity_app_settings.secret == settings.default_secret:
    logger.warning("App is using default secret which is uploaded to the GitHub repo. ")
    logger.warning("Change it to a strong secret in production.")

if identity_app_settings.rsa_pri_key == settings.default_rsa_pri_key:
    logger.warning(
        "App is using default rsa keys which is uploaded to the GitHub repo. "
    )
    logger.warning("Change it to a strong secret in production.")
