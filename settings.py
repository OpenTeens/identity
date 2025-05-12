from random import Random
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

rand = Random("7ytgfvbghy")  # 保证每次运行都使用同一个默认 secret

# 默认密钥会出现在GitHub仓库中因此绝对不可以用于生产环境
default_secret = rand.randbytes(128 // 2).hex()
default_rsa_pri_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAz54uJlextjrKJPOE5uQMT2XvJxMMBdRL+A92u1Cyv2cA24Zq\nIiiByEXiE/GdXRUXx77gdmLlWsq1FiRlRWmJA2X3XAqIhqKv8Cpf33YTTQzILfx1\nlKIht+Se7EplGYDc/ouX2GvXvzhkg3p4UO87KEXMAtOgiyZIZhpIlQgGi+6MRyFH\nRQTpeLfrERQjEOIuY2ArfVz/9p5ZRWGl2cHA9CTHuxEUSy2Eqzq4mx2ncnKnvS4v\n7jTg3/ji2ezqd2fmu9ulntMDzhfu9Y+wYInfDsP1y5yuTBet65nbqFFyyLavG3Pd\nPx3aMrevioXD7f2IE/XmCjY/8WqXztK2fOX7JQIDAQABAoIBAAHlvT3jMisGMvG0\nAfY4dyHzeZf+RIzXeQZXtRFKhlbA5IYEd0nOqtkgqBCHjtB6cZUipljuBBpRLkl0\nOpUXc00gqy87Nt/H97rGm7+8bjA5+57mRu6V/IJ6hLH+P/xSs6YIbcELCAl78Qyb\nQJmCwZVSiw158f8bj3C1v6sHAic7LctwMA+KDqjAl4+E0OdUQFch/RwEJQQUsnL5\n0C6sdE87kMJwFsCq6rO+JM4Z/ffP7cRytEr1TNn70pJD9Bmp7Mo5UO2SfM2sg4KN\niQ4JUKys5SelNYTssyGxfVliVh04v85L4Slji2qn73W1Jh+MIkI1TRvzOR9DWE0T\ndPGHD8kCgYEA2ojLwX5KoZ3re1LuDqGhpagy0/f3m01NloMagAMCxb8AZsdxk61p\nPKU0LIpJsdgqK7tuFSU6tY5iEGbaZ1sJiRhaCzYLHI25cg+uAgf5cgg0ql+N/kn2\njug6wBj1NAxv+xKF28ywPIoX0m+9ifeXWVsrOFycfxpZCMzYoT0ju40CgYEA8zZG\nJv9Z/DeKPd45oFgrwab47b+6ne4DsGV3BnZDZfdb/vjulYpnIn+gcGRtDYxBWT/Y\nZcK/g16EqGjejknnGjtTm2ThOT0ozyXcMZDurjYUmVXCF7DkR7ipMHmwJtMNuKjS\nF+MMI+5KnBFCKatkYhRsUCWDqTTV7Ct3VVxLi/kCgYB2UnLgBR0rfHGviCtUyLbZ\nFsTOeAgckjJcOAf1H6w0nUH+ZCZeqxm7uEcThpx4Km5K12S3Fj0/aCQ4dTfzlhsH\nm6PFRjGl+CZcV5kDiIXK9B5v0OT0td9FaP/GWr0IvWM0McdARwd0/9/+FHovZVsR\nCofQMHSbbQyf8ymnw47BUQKBgQDKm/gtHKSWHJ6pk6tmDI3HMZZGWWbZkiK4nI5f\nb74N/9c/vZjkMvxgHPpHJyJCGwmFlE5t16M7iU3yDgr5dk9z5uBrn8qQqIaKqvuY\nvyhXMO5QHsUmf1Js/UTVAUrhzQitQNZk19yRQj4dbbM0i3eAzYq96cKY/08HA97R\n2aWF4QKBgEkc9wn+okBM076GilozaGir0xdl2DHxjvVzXef1mWrg9VOyA5AfM58o\nVruJkIXDYlTI2ttU9QSdtSoMfemoMYhnUphFx/2Q3DDBFZ09V57BW+o6gCmHVTld\nI5N3Hq6EW/b1YM0n06iBE6IVRvZ1PmOJGs7OVdLdGVojQE8zNGKn\n-----END RSA PRIVATE KEY-----"
default_rsa_pub_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz54uJlextjrKJPOE5uQM\nT2XvJxMMBdRL+A92u1Cyv2cA24ZqIiiByEXiE/GdXRUXx77gdmLlWsq1FiRlRWmJ\nA2X3XAqIhqKv8Cpf33YTTQzILfx1lKIht+Se7EplGYDc/ouX2GvXvzhkg3p4UO87\nKEXMAtOgiyZIZhpIlQgGi+6MRyFHRQTpeLfrERQjEOIuY2ArfVz/9p5ZRWGl2cHA\n9CTHuxEUSy2Eqzq4mx2ncnKnvS4v7jTg3/ji2ezqd2fmu9ulntMDzhfu9Y+wYInf\nDsP1y5yuTBet65nbqFFyyLavG3PdPx3aMrevioXD7f2IE/XmCjY/8WqXztK2fOX7\nJQIDAQAB\n-----END PUBLIC KEY-----"


class IdentityAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            ".dev.env",
            ".prod.env",
            ".secrets.env",
        ]
    )

    @model_validator(mode="after")
    def check_secret(self) -> Self:
        if self.is_prod and self.secret == default_secret:
            raise ValueError("Secret cannot be default in production")  # noqa: TRY003
        return self

    is_prod: bool = False
    secret: str = Field(min_length=128, default=default_secret)
    db_conn_url: str = Field(default="sqlite+aiosqlite:///data.db")
    rsa_pri_key: str = Field(default=default_rsa_pri_key)
    rsa_pub_key: str = Field(default=default_rsa_pub_key)
    issuer: str = Field(default="http://localhost:9000")


identity_app_settings = IdentityAppSettings()
