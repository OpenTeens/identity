import logging  # noqa: D100
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated

import argon2
import jwt
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from db_manager import engine, get_db
from db_models import Base, Code, OAuthApp, User
from settings import identity_app_settings
from utils import random_str
from utils.log_handler import MyHandler
from utils.servers import ASGIServer, detect_server


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa: D103
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)
hasher = argon2.PasswordHasher(time_cost=1, memory_cost=4096)

webserver = detect_server()
logger = logging.getLogger(__name__)

class ClientInfo(BaseModel):  # noqa: D101
    status: int = 500
    id: int = -1
    app_name: str = ""
    app_desc: str = ""
    client_id: str = ""
    allowed_scopes: str = ""
    redirect_uri: str = ""

    class Config:  # noqa: D106
        from_attributes = True


class ErrorWithDetail(BaseModel):  # noqa: D101
    detail: str = "Error details. "


@app.get(
    "/api/client/{client_id}/info",
    response_model=ClientInfo,
    responses={
        "200": {"model": ClientInfo},
        "404": {"model": ErrorWithDetail},
    },
)
async def client_info(  # noqa: D103
    client_id: str, db_session: AsyncSession = Depends(get_db)
) -> ClientInfo:
    stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
    result = (await db_session.execute(stmt)).one_or_none()

    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientInfo(status=200, **jsonable_encoder(result[0]))


class ApproveData(BaseModel):  # noqa: D101
    client_id: str
    redirect_uri: str
    scope: str


class CodeResponse(BaseModel):  # noqa: D101
    code: str


@app.post(
    "/api/approve_authorize",
    response_model=CodeResponse,
    responses={
        200: {"model": CodeResponse},
        401: {"model": ErrorWithDetail},
        403: {"model": ErrorWithDetail},
        404: {"model": ErrorWithDetail},
    },
)
async def approve_authorize(  # noqa: D103
    data: ApproveData,
    request: Request,
    db_session: AsyncSession = Depends(get_db),
) -> CodeResponse:
    if "username" not in request.cookies:
        raise HTTPException(status_code=401, detail="Unauthorized")

    stmt = select(OAuthApp).where(OAuthApp.client_id == data.client_id)
    oauth_app_result = (await db_session.execute(stmt)).one_or_none()

    if not oauth_app_result:
        raise HTTPException(status_code=404, detail="Invalid client_id")
    oauth_app_obj: OAuthApp = oauth_app_result[0]

    code_obj = Code(
        code=random_str(32),
        client_id=data.client_id,
        scope=data.scope,
        redirect_uri=data.redirect_uri,
        access_token=random_str(32),
        id_token=jwt.encode(
            {"username": request.cookies["username"]},
            oauth_app_obj.client_secret,
            algorithm="HS256",
        ),
    )
    db_session.add(code_obj)
    code = code_obj.code

    await db_session.commit()

    return CodeResponse(code=code)


class TokenResponse(BaseModel):  # noqa: D101
    access_token: str
    scope: str
    expires_in: int
    id_token: str | None = None


class GrantTypes(StrEnum):  # noqa: D101
    AUTHORIZATION_CODE = "authorization_code"


@app.post(
    "/api/token",
    response_model=TokenResponse,
    responses={
        200: {"model": TokenResponse},
        403: {"model": ErrorWithDetail},
        404: {"model": ErrorWithDetail},
    },
)
async def token_endpoint(  # noqa: D103
    grant_type: Annotated[GrantTypes, Form()],
    code: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    redirect_uri: Annotated[str, Form()],
    db_session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    if grant_type == GrantTypes.AUTHORIZATION_CODE:
        stmt = select(Code).where(Code.code == code)
        code_result = (await db_session.execute(stmt)).one_or_none()
        if not code_result:
            raise HTTPException(status_code=404, detail="Invalid code")
        code_obj: Code = code_result[0]
        if code_obj.client_id != client_id:
            raise HTTPException(status_code=403, detail="Invalid client_id")
        if code_obj.redirect_uri != redirect_uri:
            raise HTTPException(status_code=403, detail="Invalid redirect_uri")

        stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
        oauth_app_result = (await db_session.execute(stmt)).one_or_none()

        if not oauth_app_result:
            raise HTTPException(status_code=404, detail="Invalid client_id")
        oauth_app_obj: OAuthApp = oauth_app_result[0]
        if oauth_app_obj.client_secret != client_secret:
            raise HTTPException(status_code=403, detail="Invalid client_secret")

        resp_data = TokenResponse(
            access_token=code_obj.access_token,
            scope=code_obj.scope,
            expires_in=86400,  # 1d
        )

        if "openid" in code_obj.scope.split(" "):
            resp_data.id_token = code_obj.id_token
        return resp_data

    else:
        raise HTTPException(status_code=404, detail="Unsupported grant_type")


# TODO: Data validation
class RegisterReq(BaseModel):  # noqa: D101
    username: str
    password: str
    email: str
    nickname: str


class LoginReq(BaseModel):  # noqa: D101
    login: str
    password: str


# class SuccessOrReason(BaseModel):
#     success: bool
#     reason: str


class AuthTokenResponse(BaseModel):  # noqa: D101
    token: str


class AuthTokenPayload(BaseModel):  # noqa: D101
    user_id: int
    created_at: float
    expire_at: float


@app.post(
    "/api/register",
    response_model=AuthTokenResponse,
    responses={
        200: {"model": AuthTokenResponse},
        403: {"model": ErrorWithDetail},
        409: {"model": ErrorWithDetail},
    },
)
async def register(  # noqa: D103
    register_req: RegisterReq,
    response: Response,
    db_session: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    # Check if username exists
    stmt = select(1).where(User.username == register_req.username)
    result = (await db_session.execute(stmt)).scalar()
    if result:
        raise HTTPException(status_code=409, detail="Username exists")

    # Check if email exists
    stmt = select(1).where(User.email == register_req.email)
    result = (await db_session.execute(stmt)).scalar()
    if result:
        raise HTTPException(status_code=409, detail="Email exists")

    hashed_password = hasher.hash(register_req.password)

    new_user = User(
        username=register_req.username,
        email=register_req.email,
        nickname=register_req.nickname,
        hashed_password=hashed_password,
        joined_at=datetime.now(),
    )

    db_session.add(new_user)
    await db_session.flush()

    token_payload = AuthTokenPayload(
        user_id=new_user.id,
        created_at=datetime.now().timestamp(),
        expire_at=(datetime.now() + timedelta(days=7)).timestamp(),
    )

    await (
        db_session.commit()
    )  # Commit as soon as possible to avoid conflicts and rollback

    token = jwt.encode(
        token_payload.model_dump(),
        identity_app_settings.secret,
        algorithm="HS256",
    )

    response.set_cookie("token", token)
    return AuthTokenResponse(token=token)


@app.post(
    "/api/login",
    response_model=AuthTokenResponse,
    responses={
        200: {"model": AuthTokenResponse},
        401: {"model": ErrorWithDetail},
    },
)
async def login(  # noqa: D103
    login_req: LoginReq, response: Response, db_session: AsyncSession = Depends(get_db)
) -> AuthTokenResponse:
    stmt = select(User).where(
        (User.username == login_req.login) | (User.email == login_req.login)
    )
    result = (await db_session.execute(stmt)).scalar()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        hasher.verify(result.hashed_password, login_req.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid credentials") from None

    token_payload = AuthTokenPayload(
        user_id=result.id,
        created_at=datetime.now().timestamp(),
        expire_at=(datetime.now() + timedelta(days=7)).timestamp(),
    )

    token = jwt.encode(
        token_payload.model_dump(),
        identity_app_settings.secret,
        algorithm="HS256",
    )

    response.set_cookie("token", token)
    return AuthTokenResponse(token=token)


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

