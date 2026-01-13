from typing import List
from app.db.repositories.chat_session_repo import ChatSessionRepository
from app.schemas.chat_session import ChatSessionCreate
from app.db.models.chat_session import ChatSession

class ChatSessionService:

    @staticmethod
    async def create_session(payload: ChatSessionCreate) -> ChatSession:
        return ChatSessionRepository.create(payload)

    @staticmethod
    async def get_session_by_id(ch_id: int) -> ChatSession | None:
        return ChatSessionRepository.get_by_id(ch_id)

    @staticmethod
    async def list_sessions_by_user(u_id: int) -> List[ChatSession]:
        return ChatSessionRepository.list_by_user(u_id)

    @staticmethod
    async def update_session_status(ch_id: int, status: str) -> ChatSession | None:
        return ChatSessionRepository.update_status(ch_id, status)
