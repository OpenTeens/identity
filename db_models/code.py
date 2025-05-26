from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db_models.base import Base


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
