from enum import StrEnum
from typing import Annotated, Callable, Any, Awaitable, Literal

import argon2
import jwt
from fastapi import FastAPI, Request, Response, status, Form, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, model_serializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_manager import engine, get_db
from db_models import Base, User, OAuthApp, Code
from utils import random_str

app = FastAPI()
hasher = argon2.PasswordHasher(time_cost=1, memory_cost=4096)


@app.on_event("startup")
async def refresh_token():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class ClientInfo(BaseModel):
    id: int = -1
    app_name: str = ""
    app_desc: str = ""
    client_id: str = ""
    allowed_scopes: str = ""
    redirect_uri: str = ""

    class Config:
        from_attributes = True


class ErrorWithDetail(BaseModel):
    status_code: int = 400
    detail: str = "Error details. "

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise HTTPException(status_code=self.status_code, detail=self.detail)


@app.get(
    "/api/client/{client_id}/info",
    response_model=ClientInfo,
    responses={
        "200": {"model": ClientInfo},
        "404": {"model": ErrorWithDetail},
    },
)
async def client_info(
    client_id: str, db_session: AsyncSession = Depends(get_db)
) -> ClientInfo | ErrorWithDetail:
    stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
    result = (await db_session.execute(stmt)).one_or_none()

    if not result:
        return ErrorWithDetail(status_code=404, detail="Client not found")
    return ClientInfo(**jsonable_encoder(result[0]))


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
    db_session: AsyncSession = Depends(get_db),
) -> CodeResponse | ErrorWithDetail:
    if "username" not in request.cookies:
        return ErrorWithDetail(status_code=401, detail="Unauthorized")

    stmt = select(OAuthApp).where(OAuthApp.client_id == data.client_id)
    oauth_app_result = (await db_session.execute(stmt)).one_or_none()

    if not oauth_app_result:
        return ErrorWithDetail(status_code=404, detail="Invalid client_id")
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
async def token(
    grant_type: Annotated[GrantTypes, Form()],
    code: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    redirect_uri: Annotated[str, Form()],
    db_session: AsyncSession = Depends(get_db),
) -> TokenResponse | ErrorWithDetail:
    if grant_type == GrantTypes.AUTHORIZATION_CODE:
        stmt = select(Code).where(Code.code == code)
        code_result = (await db_session.execute(stmt)).one_or_none()
        if not code_result:
            return ErrorWithDetail(status_code=404, detail="Invalid code")
        code_obj: Code = code_result[0]
        if code_obj.client_id != client_id:
            return ErrorWithDetail(status_code=403, detail="Invalid client_id")
        if code_obj.redirect_uri != redirect_uri:
            return ErrorWithDetail(status_code=403, detail="Invalid redirect_uri")

        stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
        oauth_app_result = (await db_session.execute(stmt)).one_or_none()

        if not oauth_app_result:
            return ErrorWithDetail(status_code=404, detail="Invalid client_id")
        oauth_app_obj: OAuthApp = oauth_app_result[0]
        if oauth_app_obj.client_secret != client_secret:
            return ErrorWithDetail(status_code=403, detail="Invalid client_secret")

        resp_data = TokenResponse(
            access_token=code_obj.access_token,
            scope=code_obj.scope,
            expires_in=86400,  # 1d
        )

        if "openid" in code_obj.scope.split(" "):
            resp_data.id_token = code_obj.id_token
        return resp_data

    else:
        return ErrorWithDetail(status_code=404, detail="Unsupported grant_type")


#
# # TODO: Data validation
# class RegisterReq(BaseModel):
#     username: str
#     password: str
#     email: str
#     nickname: str
#
#
# class LoginReq(BaseModel):
#     login: str
#     password: str
#
#
# class SuccessOrReason(BaseModel):
#     success: bool
#     reason: str
#
#
# @app.post("/api/register")
# async def register(
#     register_req: RegisterReq, db_session: AsyncSession = Depends(get_db)
# ):
#     # Check if username exists
#     stmt = select(1).where(User.username == register_req.username)
#     result = (await db_session.execute(stmt)).scalar()
#     print(result)
#     # Check if email exists
#
#     hashed_password = hasher.hash(register_req.password)
#
#     new_user = User(
#         username=register_req.username,
#         email=register_req.email,
#         nickname=register_req.nickname,
#         hashed_passwd=hashed_password,
#     )
#
#     db_session.add(new_user)
#     await db_session.commit()
#     return {"success": True}
#
#
# @app.post("/api/login")
# async def login(login_req: LoginReq): ...
