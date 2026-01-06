from enum import Enum

from pydantic_settings import SettingsConfigDict

from .deploy import DeploymentConfig
from .middleware import MiddlewareConfig
from .packaging import PackagingInfo

class Environment(str, Enum):
    """Application environment types.

    Defines the possible environments the application can run in:
    development, staging, production, and test.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

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