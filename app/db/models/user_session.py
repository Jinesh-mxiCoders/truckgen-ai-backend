from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from app.core.database import Base
from sqlalchemy.sql import func

class UserSession(Base):
    __tablename__ = "user_sessions"

    us_id = Column(Integer, primary_key=True, index=True)
    u_id = Column(Integer, ForeignKey("users.u_id", ondelete="CASCADE"), nullable=False)

    refresh_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
