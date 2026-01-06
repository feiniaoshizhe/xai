"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/6 15:32
Description:
FilePath: base
"""
from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC), sa_column_kwargs={"onupdate": datetime.now(UTC)}
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))