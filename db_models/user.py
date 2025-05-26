import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db_models.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Basic Auth Info
    username: Mapped[str] = mapped_column(String(16))
    hashed_password = mapped_column(String(128))  # Use Argon2id

    # Adv Auth Info
    email: Mapped[str] = mapped_column(String(32))

    # Account Status
    activated: Mapped[bool] = mapped_column(default=False)
    read_only: Mapped[bool] = mapped_column(default=False)
    can_login: Mapped[bool] = mapped_column(default=True)
    shadow_banned: Mapped[bool] = mapped_column(default=False)  # Reserved Column

    # Personal Info
    nickname: Mapped[str] = mapped_column(String(32))
    avatar_url: Mapped[str | None] = mapped_column(String(96))
    bio: Mapped[str | None] = mapped_column(Text())
    birth: Mapped[datetime.date | None]
    joined_at: Mapped[datetime.datetime]
    website: Mapped[str | None] = mapped_column(String(64))
    phone: Mapped[str | None] = mapped_column(String(16))

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username={self.username}, "
            f"activated={self.activated})>"
        )
