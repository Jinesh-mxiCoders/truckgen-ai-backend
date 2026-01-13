from sqlalchemy.orm import Session
from typing import List
from app.db.models.chat_message import ChatMessage
from app.schemas.chat_message import ChatMessageCreate
from app.core.session_manager import use_db

class ChatMessageRepository:

    @staticmethod
    @use_db
    def create(payload: ChatMessageCreate, db: Session) -> ChatMessage:
        message = ChatMessage(**payload.dict())
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    @use_db
    def list_by_chat_session(cs_id: int, db: Session) -> List[ChatMessage]:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.cs_id == cs_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    @staticmethod
    @use_db
    def list_all_message(cs_id: int, db: Session) -> List[ChatMessage]:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.cs_id == cs_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )