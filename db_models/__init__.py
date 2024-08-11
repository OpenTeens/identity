from .base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    hashed_passwd = mapped_column(String(128))

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"


class OAuthApp(Base):
    __tablename__ = "oauth_apps"
    id: Mapped[int] = mapped_column(primary_key=True)
    app_name: Mapped[str] = mapped_column(String(30))
    app_desc: Mapped[str] = mapped_column(String(256))
    client_id: Mapped[str] = mapped_column(String(32), unique=True)
    client_secret: Mapped[str] = mapped_column(String(32))
    redirect_uri: Mapped[str] = mapped_column(String(256))
    allowed_scopes: Mapped[str] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"<OAuthApp(client_id={self.client_id})>"


class Code(Base):
    __tablename__ = "codes"
    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(32))
    scope: Mapped[str] = mapped_column(String(256))
    redirect_uri: Mapped[str] = mapped_column(String(256))
    access_token: Mapped[str] = mapped_column(String(32))
    id_token: Mapped[str] = mapped_column(String(1024))

    def __repr__(self) -> str:
        return f"<Code(code={self.code})>"
