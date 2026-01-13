from sqlalchemy import Column, String, DateTime, Boolean, Integer
from app.core.database import Base
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"

    u_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    name = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
