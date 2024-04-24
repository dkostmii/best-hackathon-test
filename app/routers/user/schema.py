from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: UUID
    username: str
    date_joined: datetime
    is_staff: bool
    is_deleted: bool


class UserRegistrationSchema(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    is_staff: bool = False


class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
