from random import Random
from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


rand = Random("7ytgfvbghy")  # 保证每次运行都使用同一个默认 secret
default_secret = rand.randbytes(
    128 // 2
).hex()  # 默认密钥会出现在GitHub仓库中因此绝对不可以用于生产环境


class IdentityAppSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            ".prod.env",
            ".secrets.env",
        ]
    )

    @model_validator(mode="after")
    def check_secret(self) -> Self:
        if self.is_prod and self.secret == default_secret:
            raise ValueError("Secret cannot be default in production")
        return self

    is_prod: bool = False
    secret: str = Field(min_length=128, default=default_secret)


identity_app_settings = IdentityAppSettings()
