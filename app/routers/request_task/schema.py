from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

# from app.routers.user.schema import UserSchema


class PrioritySchema(BaseModel):
    id: int
    name: str


class RequestTaskCreateSchema(BaseModel):
    priority_id: int
    name: str
    description: str
    ending_at: datetime | None
    location_lng_lat: str | None


class RequestTaskSchema(RequestTaskCreateSchema):
    id: UUID
