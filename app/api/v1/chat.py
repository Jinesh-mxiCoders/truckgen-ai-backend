from fastapi import APIRouter, HTTPException, Request
from app.schemas.chat import ChatRequest, ChatResponse
from app.conversation.state.session_store import SessionStore
from app.conversation.engine import ConversationEngine
from app.conversation.contracts import EngineAction
from app.spec_provider.json_provider import JsonModelSpecProvider
from pathlib import Path
from app.services.image_service import ImageService
from app.conversation.state.states import ConversationStage
from app.utils.response_builder import ResponseBuilder
from app.schemas.api_response import APIResponse
from app.db.repositories.chat_session_repo import ChatSessionRepository
from app.modules.chat_session.chat_session_service import ChatSessionService
from app.modules.chat_message.chat_message_service import ChatMessageService
from app.modules.chat.chat_service import ChatService

router = APIRouter(tags=["Chat"])
session_store = SessionStore()

@router.post("", response_model=APIResponse)
async def chat(payload: ChatRequest, req: Request):
    try:
        user_id = int(req.state.user_id)

        chat_service = ChatService(user_id=user_id)
        chat_response = await chat_service.handle_message(payload)

        return ResponseBuilder.success(chat_response, "Chat processed successfully")

    except Exception as e:
        print("CHAT ERROR:", e)
        return ResponseBuilder.error(
            "Internal server error while processing chat",
            code=500
        )
 
@router.get("/sessions")
async def getChatSession(req:Request):
    try:
        user_id = int(req.state.user_id)
        chat_sessions = await ChatSessionService.list_sessions_by_user(user_id)
        return ResponseBuilder.success(chat_sessions, "Chat session fetched successfully")
    
    except Exception as e:
        print("CHAT SESSION:", e)
        return ResponseBuilder.error("Internal server error while fetching chat histroy", code=500)

@router.get("/{session_id}/history")
async def getChatHistory(session_id: int):
    try:
        messages = await ChatMessageService.get_messages(cs_id=session_id)
        print("type", type(messages))
        return ResponseBuilder.success(messages, "Chat session fetched successfully")
    
    except Exception as e:
        return ResponseBuilder.error(
            "Internal server error while processing chat",
            code=500
        )
    



# @router.post("/chat", response_model=APIResponse)
# async def chat(payload: ChatRequest, req:Request):
#     try:
#         user_id = int(req.state.user_id)
#         if not payload.session_id:
#             session, session_id = session_store.create_session()
#             chat_session = ChatSessionRepository.create_chat_session(
#                 user_id=user_id,
#                 cb_id=1,
#                 redis_key=session_id
#             )
#             payload.session_id = chat_session.cs_id
#             print(f"[INFO] Created new session: {payload.session_id}")
        
#         chat_session = ChatSessionRepository.get_chat_session(cs_id=payload.session_id)
#         session = session_store.get_session(chat_session.redis_key)

#         session.setdefault("messages", [])
#         session["messages"].append({
#             "role": "user",
#             "content": {
#                 "text": payload.message,
#                 "image": None,
#                 "data": None
#             }
#         })

#         print("stage " , session["stage"])
#         print("product", session["product"])
#         print("data", session["data"])

#         engine_response = await ConversationEngine().process(session, payload.message)
#         print("engine_response" ,engine_response)

#         if engine_response.action == EngineAction.WELCOME:
#             data=["Stationary Pumps", "Boom Pumps", "Loop Belts", "Placing Booms"]
#             assistant_message ={
#                 "role":"assistant",
#                 "content": {
#                     "text": engine_response.message,
#                     "image": None,
#                     "data": {
#                         "type":"list",
#                         "value":data
#                     }
#                 }
#             }
            
#             session["stage"] = ConversationStage.PRODUCT_SELECTION
#             session["messages"].append(assistant_message)
#             session_store.update_session(chat_session.redis_key, session)

#             chat_response = ChatResponse(
#                 reply=assistant_message,
#                 stage=session.get("stage"),
#                 session_id=payload.session_id
#             )

#             return ResponseBuilder.success(chat_response, "Welcome message sent")

#         if engine_response.action == EngineAction.ASK or engine_response.action == EngineAction.REPLY or engine_response.action == EngineAction.INVALID:
#             assistant_message ={
#                 "role":"assistant",
#                 "content": {
#                     "text": engine_response.message,
#                     "image": None,
#                     "data": None
#                 }
#             }
#             session["messages"].append(assistant_message)
#             session_store.update_session(chat_session.redis_key, session)

#             chat_response =  ChatResponse(
#                 reply=assistant_message,
#                 stage=session["stage"],
#                 product=session["product"],
#             )

#             return ResponseBuilder.success(chat_response, "Message from assistant")

#         if engine_response.action == EngineAction.MODEL_RECOMMENDATION:
#             # fetchiing sepcs of recommended models
#             models_list = engine_response.payload.get("models_list", [])
#             TRUCK_SPEC_JSON_PATH = Path("app/rag/data/truck_spec.json")
#             specifications = JsonModelSpecProvider(json_path=TRUCK_SPEC_JSON_PATH).get_specs_by_models(
#                 product_type=session["product"],
#                 model_names=models_list
#             )

#             session["recommend_models"] = models_list
#             session["models"] = engine_response.payload.get("selected_model")
#             assistant_message = {
#                 "role": "assistant",
#                 "content": {
#                     "text": engine_response.message,
#                     "image": None,
#                     "data": {
#                         "type":"table",
#                         "value" : specifications
#                     }
#                 }
#             }
#             session["messages"].append(assistant_message)
#             session_store.update_session(chat_session.redis_key, session)

#             chat_response = ChatResponse(
#                 reply=assistant_message,
#                 stage=session["stage"],
#                 product=session["product"],
#                 data=session["data"],
#                 result=specifications,
#                 recommend_models=session["recommend_models"]
#             )

#             return ResponseBuilder.success(chat_response, "Model recommendations sent")

#         if engine_response.action == EngineAction.MODEL_SELECTED:
#             model = engine_response.payload["model"]

#             # store selection
#             session["selected_models"] = model
#             session["stage"] = ConversationStage.MODEL_SELECTED

#             images = ImageService().get_primary_image(model)

#             assistant_message ={
#                 "role": "assistant",
#                 "content": {
#                     "text": engine_response.message,
#                     "image": images,
#                     "data": None
#                 }
#             }
#             session["messages"].append(assistant_message)
#             session["stage"] =  ConversationStage.COMPLETE

#             session_store.update_session(chat_session.redis_key, session)

#             chat_response = ChatResponse(
#                 reply=assistant_message,
#                 stage=session["stage"],
#                 product=session["product"],
#             )
#             return ResponseBuilder.success(chat_response, "Model selected")

#         if engine_response.action == EngineAction.COMPLETE:
#             assistant_message ={
#                 "role": "assistant",
#                 "content": {
#                     "text": engine_response.message,
#                     "image": None,
#                     "data": None
#                 }
#             }
#             session["messages"].append(assistant_message)
#             session["stage"] = ConversationStage.COMPLETE
#             session_store.update_session(chat_session.redis_key, session)

#             chat_response = ChatResponse(
#                 reply=assistant_message,
#                 completed=True,
#                 stage=session["stage"],
#                 product=session["product"],
#                 data=None,
#             )

#             return ResponseBuilder.success(chat_response, "Conversation completed")

#         return ResponseBuilder.error("Unknown engine action", code=500)

#     except Exception as e:
#         print("CHAT ERROR:", e)
#         return ResponseBuilder.error("Internal server error while processing chat", code=500)

# @router.get("/chat/{session_id}/history")
# async def getChatHistory(session_id: str):
#     try:
#         session = session_store.get_session(session_id)
#         messages = session.get("messages")
#         return ResponseBuilder.success(messages, "Chat history fetched successfully")
    
#     except Exception as e:
#         print("CHAT HISTORY:", e)
#         return ResponseBuilder.error("Internal server error while fetching chat histroy", code=500)
