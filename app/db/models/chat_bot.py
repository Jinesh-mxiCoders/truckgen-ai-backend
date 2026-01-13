from sqlalchemy import Column, String, Text, TIMESTAMP, Integer
from sqlalchemy.sql import func
from app.core.database import Base

class ChatBot(Base):
    __tablename__ = "chat_bot"

    cb_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
