import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import settings
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app.instance import app as app
from app.instance import logger
from db_manager import engine
from db_models import Base
from settings import identity_app_settings
from utils.log_handler import MyHandler
from utils.servers import ASGIServer, detect_server


class SchemaMismatchError(Exception):
    """DB schema does not match SQLAlchemy models."""

    def __init__(self, diffs: list) -> None:
        super().__init__(
            f"{diffs}\n"
            "❌ Detected database schema differences. Did you forget to run migrations?\n"
        )


async def ensure_db_schema_consistency() -> None:
    async with engine.connect() as connection:
        context = await connection.run_sync(
            MigrationContext.configure,
            url=identity_app_settings.db_conn_url,
            dialect_opts={"paramstyle": "named"},
        )

        diffs = await connection.run_sync(
            lambda _: compare_metadata(context, Base.metadata)
        )

    if diffs:
        raise SchemaMismatchError(diffs)


inner_lifespan = app.router.lifespan_context


@asynccontextmanager
async def main_lifespan(application: FastAPI) -> AsyncGenerator:
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    await ensure_db_schema_consistency()

    async with inner_lifespan(application):
        yield


app.router.lifespan_context = main_lifespan


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
