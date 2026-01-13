from app.db.models.chat_bot import ChatBot
from app.schemas.chat_bot import ChatBotCreate
from app.core.session_manager import use_db
from sqlalchemy.orm import Session

class ChatBotRepository:

    @staticmethod
    @use_db
    def create(payload: ChatBotCreate, db:Session):
        bot = ChatBot(**payload.dict())
        db.add(bot)
        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    @use_db
    def get_by_id(cb_id: int, db:Session):
        return db.query(ChatBot).filter(ChatBot.cb_id == cb_id).first()

    @staticmethod
    @use_db
    def list_all(db:Session):
        return db.query(ChatBot).all()
