from __future__ import annotations

import base64
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from functools import lru_cache
from typing import Annotated, Literal

import argon2
import jwt
from argon2.exceptions import VerifyMismatchError
from Crypto.PublicKey import RSA
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings as settings
from db_manager import engine, get_db
from db_models import Base, Code, OAuthApp, User
from settings import identity_app_settings
from utils.log_handler import MyHandler as MyHandler
from utils.randoms import random_str
from utils.servers import ASGIServer as ASGIServer
from utils.servers import detect_server as detect_server


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)
hasher = argon2.PasswordHasher(time_cost=1, memory_cost=4096)
logger = logging.getLogger(__name__)
tz = datetime.now(UTC).astimezone().tzinfo


class OpenIDConfig(BaseModel):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str


@app.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> OpenIDConfig:
    host = request.headers.get("Host")
    return OpenIDConfig(
        issuer=identity_app_settings.issuer,
        authorization_endpoint=f"https://{host}/#/authorize",
        token_endpoint=f"https://{host}/api/token",
        userinfo_endpoint=f"https://{host}/api/userinfo",
        jwks_uri=f"https://{host}/.well-known/jwks.json",
    )


class JWKBase(BaseModel):
    kty: Literal["RSA", "EC", "oct"]
    use: Literal["enc", "sig"]
    alg: str | None = None
    kid: str | None = None


class JWKEc(JWKBase):
    kty: Literal["RSA", "EC", "oct"] = "EC"
    alg: str | None = "ES256"
    crv: str
    x: str
    y: str
    d: str | None = None


class JWKRsa(JWKBase):
    kty: Literal["RSA", "EC", "oct"] = "RSA"
    alg: str | None = "RS256"
    n: str
    e: str
    d: str | None = None


class JWKs(BaseModel):
    keys: list[JWKEc | JWKRsa]


@lru_cache
def get_rsa_key_params() -> tuple[int, int]:
    key = get_ec_pri_key()
    return key.n, key.e


@lru_cache
def get_ec_pri_key() -> RSA.RsaKey:
    return RSA.import_key(identity_app_settings.rsa_pri_key)


@lru_cache
def int_to_base64_octet_string(num: int) -> str:
    length = num.bit_length()
    bytes_length = (length + 7) // 8
    return (
        base64.urlsafe_b64encode(num.to_bytes(bytes_length, "big"))
        .rstrip(b"=")
        .decode()
    )


@app.get("/.well-known/jwks.json")
async def get_jwks() -> JWKs:
    params = get_rsa_key_params()
    return JWKs(
        keys=[
            JWKRsa(
                kid="main",
                use="sig",
                n=int_to_base64_octet_string(int(params[0])),
                e=int_to_base64_octet_string(int(params[1])),
            )
        ]
    )


class ClientInfo(BaseModel):
    status: int = 500
    id: int = -1
    app_name: str = ""
    app_desc: str = ""
    app_icon_url: str | None = ""
    client_id: str = ""
    allowed_scopes: str = ""
    redirect_uri: str = ""
    model_config = ConfigDict(from_attributes=True)


class ErrorWithDetail(BaseModel):
    detail: str = "Error details. "


@app.get(
    "/api/client/{client_id}/info",
    response_model=ClientInfo,
    responses={
        "200": {"model": ClientInfo},
        "404": {"model": ErrorWithDetail},
    },
)
async def client_info(
    client_id: str,
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> ClientInfo:
    stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
    result = (await db_session.execute(stmt)).one_or_none()

    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientInfo(status=200, **jsonable_encoder(result[0]))


class ApproveData(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str


class CodeResponse(BaseModel):
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
async def approve_authorize(
    data: ApproveData,
    request: Request,
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> CodeResponse:
    if "token" not in request.cookies:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        decoded = jwt.decode(
            request.cookies["token"],
            key=identity_app_settings.rsa_pub_key,
            algorithms=["RS256"],
        )
    except jwt.InvalidSignatureError as e:
        raise HTTPException(status_code=401, detail="Token invalid") from e
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token expired") from e

    user_id = decoded["user_id"]

    stmt = select(OAuthApp).where(OAuthApp.client_id == data.client_id)
    oauth_app_result = (await db_session.execute(stmt)).one_or_none()

    if not oauth_app_result:
        raise HTTPException(status_code=404, detail="Invalid client_id")
    _oauth_app_obj: OAuthApp = oauth_app_result[0]

    code_obj = Code(
        code=random_str(32),
        client_id=data.client_id,
        scope=data.scope,
        redirect_uri=data.redirect_uri,
        access_token=random_str(32),
        id_token=jwt.encode(
            {"user_id": user_id},
            key=identity_app_settings.rsa_pri_key,
            algorithm="RS256",
            headers={"kid": "main"},
        ),
    )
    db_session.add(code_obj)
    code = code_obj.code

    await db_session.commit()

    return CodeResponse(code=code)


class TokenResponse(BaseModel):
    access_token: str
    scope: str
    expires_in: int
    id_token: str | None = None


class GrantTypes(StrEnum):
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
async def token_endpoint(
    grant_type: Annotated[GrantTypes, Form()],
    code: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    redirect_uri: Annotated[str, Form()],
    db_session: Annotated[AsyncSession, Depends(get_db)],
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

    raise HTTPException(status_code=404, detail="Unsupported grant_type")


# TODO @cxzlw: Data validation
# https://


class RegisterReq(BaseModel):
    username: str
    password: str
    email: str
    nickname: str


class LoginReq(BaseModel):
    login: str
    password: str


class AuthTokenResponse(BaseModel):
    token: str


class TokenPayload(BaseModel):
    iat: int | datetime | None = None
    nbf: int | datetime | None = None
    exp: int | datetime | None = None
    iss: str | None = None
    aud: list[str] | None = None


class AuthTokenPayload(TokenPayload):
    user_id: int


@app.post(
    "/api/register",
    response_model=AuthTokenResponse,
    responses={
        200: {"model": AuthTokenResponse},
        403: {"model": ErrorWithDetail},
        409: {"model": ErrorWithDetail},
    },
)
async def register(
    register_req: RegisterReq,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_db)],
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
        joined_at=datetime.now(tz=tz),
    )

    db_session.add(new_user)
    await db_session.flush()

    now = datetime.now(tz=tz)

    token_payload = AuthTokenPayload(
        user_id=new_user.id,
        iss=identity_app_settings.issuer,
        iat=now,
        nbf=now,
        exp=now + timedelta(days=7),
    )

    await (
        db_session.commit()
    )  # Commit as soon as possible to avoid conflicts and rollback

    token = jwt.encode(
        token_payload.model_dump(),
        key=identity_app_settings.rsa_pri_key,
        algorithm="RS256",
        headers={"kid": "main"},
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
async def login(
    login_req: LoginReq,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_db)],
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

    now = datetime.now(tz=tz)

    token_payload = AuthTokenPayload(
        user_id=result.id,
        iss=identity_app_settings.issuer,
        iat=now,
        nbf=now,
        exp=now + timedelta(days=7),
    )

    token = jwt.encode(
        token_payload.model_dump(),
        key=identity_app_settings.rsa_pri_key,
        algorithm="RS256",
        headers={"kid": "main"},
    )

    response.set_cookie("token", token)
    return AuthTokenResponse(token=token)
