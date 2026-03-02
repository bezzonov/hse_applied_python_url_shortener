from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, func, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    links = relationship("Link", back_populates="user")

class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_code = Column(String(10), unique=True, index=True)
    original_url = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    is_anonymous = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    click_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
