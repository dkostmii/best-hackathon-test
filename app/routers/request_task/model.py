import uuid

from sqlalchemy import Boolean, Column, String, DateTime, text, UUID, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from database import Base


class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class RequestTask(Base):
    __tablename__ = "request_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    creator_id = Column(UUID, ForeignKey("base_users.id"))
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=text("CURRENT_TIMESTAMP"))
    done_at = Column(DateTime, nullable=True)
    is_done = Column(Boolean, server_default=expression.false(), nullable=False)
    ending_at = Column(DateTime, nullable=True)

    creator = relationship("User")
    priority = relationship("Priority")
