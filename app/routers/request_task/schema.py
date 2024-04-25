from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.routers.user.schema import UserSchema


class PrioritySchema(BaseModel):
    id: int
    name: str


class RequestTaskSchema(BaseModel):
    id: UUID
    priority: PrioritySchema
    name: str
    description: str
    created_at: datetime
    creator: UserSchema


class RequestTaskCreateSchema(BaseModel):
    priority_id: int
    name: str
    description: str
