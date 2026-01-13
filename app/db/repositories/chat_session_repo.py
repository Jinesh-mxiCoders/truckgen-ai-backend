from sqlalchemy import asc
from sqlalchemy.orm import Session
from app.db.models.chat_session import ChatSession
from app.schemas.chat_session import ChatSessionCreate
from app.core.session_manager import use_db

class ChatSessionRepository:
    
    @staticmethod
    @use_db
    def create(payload: ChatSessionCreate, db:Session):
        session = ChatSession(**payload.dict())
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def create_chat_session(user_id: int, redis_key: str, cb_id: int = 1):
        payload = ChatSessionCreate(
            u_id=user_id,
            cb_id=cb_id,
            redis_key=redis_key
        )
        return ChatSessionRepository.create(payload)

    @staticmethod
    @use_db
    def get_chat_session(cs_id: str, db:Session):
        return (
            db.query(ChatSession)
            .filter(ChatSession.cs_id == cs_id)
            .order_by(asc(ChatSession.created_at))
            .first())
    
    @staticmethod
    @use_db
    def get_redis_key(redis_key: str, db:Session):
        return db.query(ChatSession.cs_id).filter(ChatSession.redis_key == redis_key).first()

    @staticmethod
    @use_db
    def list_by_user(u_id: int, db:Session):
        return (
            db.query(ChatSession)
            .filter(ChatSession.u_id == u_id)
            .order_by(ChatSession.created_at.desc())
            .all())
    
    @staticmethod
    @use_db
    def update_status(cs_id: int, status: str, db:Session):
        session = db.query(ChatSession).filter(ChatSession.cs_id == cs_id).first()
        if session:
            session.status = status
            db.commit()
            db.refresh(session)
        return session
