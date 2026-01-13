from pathlib import Path
from app.conversation.contracts import EngineAction
from app.conversation.state.states import ConversationStage
from app.conversation.state.session_store import SessionStore
from app.schemas.chat import ChatResponse
from app.services.image_service import ImageService
from app.spec_provider.json_provider import JsonModelSpecProvider
from app.db.repositories.chat_message_repo import ChatMessageRepository
from app.schemas.chat_message import ChatMessageCreate
from app.enums.chat import ChatRoleEnum

class ChatActionHandler:
    """
    Handles EngineAction -> ChatResponse mapping
    """

    def __init__(self, session: dict, redis_key: str, chat_session:dict):
        self.session = session
        self.redis_key = redis_key
        self.chat_session = chat_session

    def handle(self, engine_response, session_id: int) -> ChatResponse:
        try:
            action = engine_response.action

            if action == EngineAction.WELCOME:
                return self._welcome(engine_response, session_id)

            if action in (
                EngineAction.ASK,
                EngineAction.REPLY,
                EngineAction.INVALID,
            ):
                return self._basic_reply(engine_response)

            if action == EngineAction.MODEL_RECOMMENDATION:
                return self._model_recommendation(engine_response)

            if action == EngineAction.MODEL_SELECTED:
                return self._model_selected(engine_response)

            if action == EngineAction.COMPLETE:
                return self._complete(engine_response)

            raise ValueError("Unknown engine action")
        
        except Exception as e:
            print("CHAT ACTION HANDLER", e)
            raise RuntimeError(
                "ChatAction Handler error"
            ) from e


    # -----------------------------------
    # Handlers
    # -----------------------------------

    def _welcome(self, engine_response, session_id):
        products = ["Stationary Pumps", "Boom Pumps", "Loop Belts", "Placing Booms"]

        message = self._assistant_message(
            text=engine_response.message,
            data={"type": "list", "value": products}
        )

        self.session["stage"] = ConversationStage.PRODUCT_SELECTION
        self._persist()

        return ChatResponse(
            reply=message,
            stage=self.session["stage"],
            session_id=session_id
        )

    def _basic_reply(self, engine_response):
        message = self._assistant_message(engine_response.message)

        self._persist()

        return ChatResponse(
            reply=message,
            stage=self.session.get("stage"),
            product=self.session.get("product")
        )

    def _model_recommendation(self, engine_response):
        print("_model_recommendation.......")
        models = engine_response.payload.get("models_list", [])

        provider = JsonModelSpecProvider(
            json_path=Path("app/rag/data/truck_spec.json")
        )

        specs = provider.get_specs_by_models(
            product_type=self.session["product"],
            model_names=models
        )
        self.session["recommend_models"] = models

        message = self._assistant_message(
            text=engine_response.message,
            data={"type": "table", "value": specs}
        )

        self._persist()

        return ChatResponse(
            reply=message,
            stage=self.session["stage"],
            product=self.session["product"],
            result=specs,
            recommend_models=models
        )

    def _model_selected(self, engine_response):
        model = engine_response.payload["model"]
        images = ImageService().get_primary_image(model)

        self.session["selected_models"] = model
        self.session["stage"] = ConversationStage.COMPLETE

        message = self._assistant_message(
            text=engine_response.message,
            image=images
        )

        self._persist()

        return ChatResponse(
            reply=message,
            stage=self.session["stage"],
            product=self.session["product"]
        )

    def _complete(self, engine_response):
        message = self._assistant_message(engine_response.message)

        self.session["stage"] = ConversationStage.COMPLETE
        self._persist()

        return ChatResponse(
            reply=message,
            completed=True,
            stage=self.session["stage"],
            product=self.session["product"]
        )

    # -----------------------------------
    # Utilities (db)
    # -----------------------------------

    def _assistant_message(self, text, image=None, data=None):
        msg_dict = {
            "role": "assistant",
            "content": {
                "text": text,
                "image": image,
                "data": data
            }
        }

        # self.session["messages"].append(msg_dict)

        ChatMessageRepository.create(
            payload=ChatMessageCreate(
                cs_id=self.chat_session.cs_id,
                role=ChatRoleEnum.ASSISTANT,
                content=msg_dict["content"]
            )
        )

        return msg_dict

    def _persist(self):
        SessionStore().update_session(self.redis_key, self.session)
