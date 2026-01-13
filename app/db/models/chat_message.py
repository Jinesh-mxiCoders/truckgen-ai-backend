from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.sql import func
from app.core.database import Base
from app.enums.chat import ChatRoleEnum

class ChatMessage(Base):
    __tablename__ = "chat_message"

    cm_id = Column(Integer, primary_key=True, autoincrement=True)
    cs_id = Column(Integer, ForeignKey("chat_session.cs_id", ondelete="CASCADE"), nullable=False)
    role = Column(
        ENUM(
            ChatRoleEnum, 
            name="chat_role", 
            create_type=False, 
            native_enum=True, 
            values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    content = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
