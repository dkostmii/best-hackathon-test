import uuid

from sqlalchemy import Column, String, DateTime, Boolean, text, UUID
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
    request_tasks = relationship("ReqestTask", back_populates="creator")
