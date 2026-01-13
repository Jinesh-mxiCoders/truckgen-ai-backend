from typing import List
from app.db.repositories.chat_message_repo import ChatMessageRepository
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse
from app.db.models.chat_message import ChatMessage

class ChatMessageService:

    @staticmethod
    async def add_message(payload: ChatMessageCreate) -> ChatMessageResponse:
        msg = ChatMessageRepository.create(payload)
        return ChatMessageResponse.from_orm(msg)

    @staticmethod
    async def get_messages_for_session(cs_id: int) -> List[ChatMessage]:
        messages = ChatMessageRepository.list_by_chat_session(cs_id)
        return [ChatMessageResponse.from_orm(m) for m in messages]
    
    @staticmethod
    async def get_messages(cs_id: int) -> List[ChatMessage]:
        messages = ChatMessageRepository.list_by_chat_session(cs_id)
        return [ChatMessageResponse.from_orm(m) for m in messages]
