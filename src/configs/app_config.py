from pydantic_settings import BaseSettings, SettingsConfigDict

from .deploy import DeploymentConfig
from .middleware import MiddlewareConfig
from .packaging import PackagingInfo


class Settings(
    PackagingInfo,
    DeploymentConfig,

    MiddlewareConfig,
):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )


settings = Settings()