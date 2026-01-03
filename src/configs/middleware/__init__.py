import os
from typing import Any, Literal
from urllib.parse import parse_qsl, quote_plus

from pydantic import Field, NonNegativeInt, PositiveInt, computed_field, PositiveFloat
from pydantic_settings import BaseSettings


class DataBaseConfig(BaseSettings):
    # Database type selector
    DB_TYPE: Literal["postgresql", "mysql", "oceanbase", "seekdb"] = Field(
        description="Database type to use. OceanBase is MySQL-compatible.",
        default="mysql",
    )

    DB_HOST: str = Field(
        description="Hostname or IP address of the database server.",
        default="localhost",
    )

    DB_PORT: PositiveInt = Field(
        description="Port number for database connection.",
        default=3306,
    )

    DB_USERNAME: str = Field(
        description="Username for database authentication.",
        default="root",
    )

    DB_PASSWORD: str = Field(
        description="Password for database authentication.",
        default="123456",
    )

    DB_DATABASE: str = Field(
        description="Name of the database to connect to.",
        default="xagent",
    )

    DB_CHARSET: str = Field(
        description="Character set for database connection.",
        default="",
    )

    DB_EXTRAS: str = Field(
        description="Additional database connection parameters. Example: 'keepalives_idle=60&keepalives=1'",
        default="",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI_SCHEME(self) -> str:
        DB_DRIVER = {
            "postgresql": "postgresql",
            "mysql": "mysql+aiomysql",
        }

        return DB_DRIVER.get(self.DB_TYPE, "mysql+aiomysql")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        db_extras = (
            f"{self.DB_EXTRAS}&client_encoding={self.DB_CHARSET}" if self.DB_CHARSET else self.DB_EXTRAS
        ).strip("&")
        db_extras = f"?{db_extras}" if db_extras else ""
        return (
            f"{self.SQLALCHEMY_DATABASE_URI_SCHEME}://"
            f"{quote_plus(self.DB_USERNAME)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
            f"{db_extras}"
        )

    SQLALCHEMY_POOL_SIZE: NonNegativeInt = Field(
        description="Maximum number of database connections in the pool.",
        default=30,
    )

    SQLALCHEMY_MAX_OVERFLOW: NonNegativeInt = Field(
        description="Maximum number of connections that can be created beyond the pool_size.",
        default=10,
    )

    SQLALCHEMY_POOL_RECYCLE: NonNegativeInt = Field(
        description="Number of seconds after which a connection is automatically recycled.",
        default=3600,
    )

    SQLALCHEMY_POOL_USE_LIFO: bool = Field(
        description="If True, SQLAlchemy will use last-in-first-out way to retrieve connections from pool.",
        default=False,
    )

    SQLALCHEMY_POOL_PRE_PING: bool = Field(
        description="If True, enables connection pool pre-ping feature to check connections.",
        default=False,
    )

    SQLALCHEMY_ECHO: bool | str = Field(
        description="If True, SQLAlchemy will log all SQL statements.",
        default=False,
    )

    SQLALCHEMY_POOL_TIMEOUT: NonNegativeInt = Field(
        description="Number of seconds to wait for a connection from the pool before raising a timeout error.",
        default=30,
    )

    RETRIEVAL_SERVICE_EXECUTORS: NonNegativeInt = Field(
        description="Number of processes for the retrieval service, default to CPU cores.",
        default=os.cpu_count() or 1,
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict[str, Any]:
        # Parse DB_EXTRAS for 'options'
        db_extras_dict = dict(parse_qsl(self.DB_EXTRAS))
        options = db_extras_dict.get("options", "")
        connect_args = {}
        # Use the dynamic SQLALCHEMY_DATABASE_URI_SCHEME property
        if self.SQLALCHEMY_DATABASE_URI_SCHEME.startswith("postgresql"):
            timezone_opt = "-c timezone=UTC"
            if options:
                merged_options = f"{options} {timezone_opt}"
            else:
                merged_options = timezone_opt
            connect_args = {"options": merged_options}

        return {
            "pool_size": self.SQLALCHEMY_POOL_SIZE,
            "max_overflow": self.SQLALCHEMY_MAX_OVERFLOW,
            "pool_recycle": self.SQLALCHEMY_POOL_RECYCLE,
            "pool_pre_ping": self.SQLALCHEMY_POOL_PRE_PING,
            "connect_args": connect_args,
            "pool_use_lifo": self.SQLALCHEMY_POOL_USE_LIFO,
            "pool_reset_on_return": None,
            "pool_timeout": self.SQLALCHEMY_POOL_TIMEOUT,
        }

class CeleryConfig(DataBaseConfig):
    CELERY_BACKEND: str = Field(
        description="Backend for Celery task results. Options: 'database', 'redis', 'rabbitmq'.",
        default="redis",
    )

    CELERY_BROKER_URL: str | None = Field(
        description="URL of the message broker for Celery tasks.",
        default=None,
    )

    CELERY_USE_SENTINEL: bool | None = Field(
        description="Whether to use Redis Sentinel for high availability.",
        default=False,
    )

    CELERY_SENTINEL_MASTER_NAME: str | None = Field(
        description="Name of the Redis Sentinel master.",
        default=None,
    )

    CELERY_SENTINEL_PASSWORD: str | None = Field(
        description="Password of the Redis Sentinel master.",
        default=None,
    )
    CELERY_SENTINEL_SOCKET_TIMEOUT: PositiveFloat | None = Field(
        description="Timeout for Redis Sentinel socket operations in seconds.",
        default=0.1,
    )

    @computed_field
    def CELERY_RESULT_BACKEND(self) -> str | None:
        if self.CELERY_BACKEND in ("database", "rabbitmq"):
            return f"db+{self.SQLALCHEMY_DATABASE_URI}"
        elif self.CELERY_BACKEND == "redis":
            return self.CELERY_BROKER_URL
        else:
            return None

    @property
    def BROKER_USE_SSL(self) -> bool:
        return self.CELERY_BROKER_URL.startswith("rediss://") if self.CELERY_BROKER_URL else False


class MiddlewareConfig(

    CeleryConfig
):
    pass