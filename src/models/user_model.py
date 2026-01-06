"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/6 16:31
Description:
FilePath: user_model
"""
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Column,String
from sqlalchemy_utils import ChoiceType

from src.models.base import BaseModel
from src.schemas.common_schema import IGenderEnum


class UserBase(SQLModel):
    email: EmailStr = Field(sa_column=Column(String, index=True, unique=True))
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    role_id: UUID | None = Field(default=None, foreign_key="Role.id")
    phone: str | None = None
    gender: IGenderEnum | None = Field(
        default=IGenderEnum.other,
        sa_column=Column(ChoiceType(IGenderEnum, impl=String())),
    )

class User(BaseModel,UserBase, table=True):
    hashed_password: str | None = Field(default=None, nullable=False, index=True)
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )