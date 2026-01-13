from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, CheckConstraint, Integer
from sqlalchemy.sql import func
from app.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_session"

    cs_id = Column(Integer, primary_key=True, autoincrement=True)
    u_id = Column(Integer, ForeignKey("users.u_id", ondelete="CASCADE"), nullable=False)
    cb_id = Column(Integer, ForeignKey("chat_bot.cb_id", ondelete="CASCADE"), nullable=False)
    redis_key = Column(String(255), unique=True, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('active','completed','abandoned')", name="check_chat_status"),
    )
