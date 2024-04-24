import uuid

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, text, UUID
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "base_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String, nullable=False)
    date_joined = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    is_staff = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    request_tasks = relationship("RequestTask", back_populates="creator")
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    user_id = Column(UUID, ForeignKey("base_users.id"), primary_key=True)
    session_token = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="sessions")
