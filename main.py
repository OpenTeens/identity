import random
import string
import jwt
from typing import Annotated

from fastapi import FastAPI, Request, Response, status, Form, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import select
from db_models import Base, User, OAuthApp, Code

engine = create_async_engine("sqlite+aiosqlite:///data.db", echo=True, future=True,
                             connect_args={"check_same_thread": False})

session_maker = async_sessionmaker(engine)


async def get_db():
    async with session_maker() as db:
        yield db


app = FastAPI()
users = ...


@app.on_event("startup")
async def refresh_token():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def random_str(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class ClientInfo(BaseModel):
    status: int = 200
    id: int = -1
    app_name: str = ""
    app_desc: str = ""
    client_id: str = ""
    allowed_scopes: str = ""
    redirect_uri: str = ""

    class Config:
        from_attributes = True


@app.get("/api/client/{client_id}/info", response_model=ClientInfo)
async def client_info(client_id: str, response: Response, db_session: AsyncSession = Depends(get_db)):
    stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
    result = (await db_session.execute(stmt)).one_or_none()
    if not result:
        # response.status_code = 404
        return {"status": 404}
    return jsonable_encoder(result[0])


@app.get("/api/login")
async def login(username, response: Response):
    response.set_cookie(key="username", value=username)
    return 1


class ApproveData(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str


@app.post("/api/approve_authorize")
async def approve_authorize(
        data: ApproveData,
        request: Request,
        response: Response,
        db_session: AsyncSession = Depends(get_db)
):
    if "username" not in request.cookies:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {}

    stmt = select(OAuthApp).where(OAuthApp.client_id == data.client_id)
    oauth_app_result = (await db_session.execute(stmt)).one_or_none()

    if not oauth_app_result:
        return {"error": "invalid client_id"}
    oauth_app_obj: OAuthApp = oauth_app_result[0]

    code_obj = Code(
        code=random_str(32),
        client_id=data.client_id,
        scope=data.scope,
        redirect_uri=data.redirect_uri,
        access_token=random_str(32),
        id_token=jwt.encode({"username": request.cookies["username"]}, oauth_app_obj.client_secret,
                            algorithm="HS256")
    )
    db_session.add(code_obj)
    code = code_obj.code

    await db_session.commit()

    return {"code": code}


@app.post("/api/token")
async def token(
        grant_type: Annotated[str, Form()],
        code: Annotated[str, Form()],
        client_id: Annotated[str, Form()],
        client_secret: Annotated[str, Form()],
        redirect_uri: Annotated[str, Form()],
        db_session: AsyncSession = Depends(get_db)
):
    if grant_type == "authorization_code":
        stmt = select(Code).where(Code.code == code)
        code_result = (await db_session.execute(stmt)).one_or_none()
        if not code_result:
            return {"error": "invalid code"}
        code_obj: Code = code_result[0]
        if code_obj.client_id != client_id:
            return {"error": "invalid client_id"}
        if code_obj.redirect_uri != redirect_uri:
            return {"error": "invalid redirect_uri"}

        stmt = select(OAuthApp).where(OAuthApp.client_id == client_id)
        oauth_app_result = (await db_session.execute(stmt)).one_or_none()

        if not oauth_app_result:
            return {"error": "invalid client_id"}
        oauth_app_obj: OAuthApp = oauth_app_result[0]
        if oauth_app_obj.client_secret != client_secret:
            return {"error": "invalid client_secret"}

        resp_data = {
            "access_token": code_obj.access_token,
            "scope": code_obj.scope,
            "expires_in": 86400  # 1d
        }

        if "openid" in code_obj.scope.split(" "):
            resp_data["id_token"] = code_obj.id_token
        return resp_data

    else:
        return {"error": "unsupported grant_type"}
