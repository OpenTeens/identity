from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db_models.base import Base


class OAuthApp(Base):
    __tablename__ = "oauth_apps"
    id: Mapped[int] = mapped_column(primary_key=True)
    app_name: Mapped[str] = mapped_column(String(30))
    app_desc: Mapped[str] = mapped_column(String(256))
    app_icon_url: Mapped[str | None] = mapped_column(String(96))
    client_id: Mapped[str] = mapped_column(String(32), unique=True)
    client_secret: Mapped[str] = mapped_column(String(32))
    redirect_uri: Mapped[str] = mapped_column(String(256))
    allowed_scopes: Mapped[str] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"<OAuthApp(client_id={self.client_id})>"
