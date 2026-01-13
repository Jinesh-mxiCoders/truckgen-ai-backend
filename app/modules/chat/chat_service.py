from app.conversation.engine import ConversationEngine
from app.conversation.state.session_store import SessionStore
from app.conversation.handlers.chat_action_handler import ChatActionHandler
from app.db.repositories.chat_session_repo import ChatSessionRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.db.repositories.chat_message_repo import ChatMessageRepository
from app.schemas.chat_message import ChatMessageCreate
from app.enums.chat import ChatRoleEnum


class ChatService:
    """
    Orchestrates:
    - Session lifecycle
    - Conversation engine
    - Action handling
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.engine = ConversationEngine()
        self.session_store = SessionStore()

    async def handle_message(self, payload: ChatRequest) -> ChatResponse:
        try:
            chat_session, session = self._get_or_create_session(payload)

            self._append_user_message(chat_session, session, payload.message)

            engine_response = await self.engine.process(session, payload.message)

            handler = ChatActionHandler(
                session=session,
                redis_key=chat_session.redis_key,
                chat_session=chat_session
            )

            return handler.handle(
                engine_response=engine_response,
                session_id=payload.session_id
            )
        
        except Exception as e:
            print("HANDLE MESSAGE", e)
            raise RuntimeError(
                f"ChatService.handle_message failed "
                f"(user_id={self.user_id}, session_id={payload.session_id})"
            ) from e

    # -----------------------------
    # Session helpers
    # -----------------------------

    def _get_or_create_session(self, payload: ChatRequest):
        try:
            if not payload.session_id:
                session, redis_key = self.session_store.create_session()

                chat_session = ChatSessionRepository.create_chat_session(
                    user_id=self.user_id,
                    cb_id=1,
                    redis_key=redis_key
                )
                payload.session_id = chat_session.cs_id
            else:
                chat_session = ChatSessionRepository.get_chat_session(
                    cs_id=payload.session_id
                )
                session = self.session_store.get_session(chat_session.redis_key)

            session.setdefault("messages", [])
            return chat_session, session

        except Exception as e:
            print("_get_or_create_session", e)
            raise RuntimeError(
                "Failed to get or create chat session"
            ) from e

    def _append_user_message(self, chat_session: dict, session: dict, message: str):
        try:
            msg_dict = {
                "role": ChatRoleEnum.USER.value,
                "content": {
                    "text": message,
                    "image": None,
                    "data": None
                }
            }
            # session["messages"].append(msg_dict)

            # Store in database
            ChatMessageRepository.create(
                payload=ChatMessageCreate(
                    cs_id=chat_session.cs_id,
                    role=ChatRoleEnum.USER,
                    content=msg_dict["content"]
                )
            )

        except Exception as e:
            print("_append_user_message", e)
            raise RuntimeError(
                "Failed to append message"
            ) from e
 