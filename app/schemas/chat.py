from pydantic import BaseModel
from typing import Dict, Any, Optional, Literal

class MessageContent(BaseModel):
    text: Optional[str] = None
    image: Optional[list[str]] = None
    data: Optional[dict] = None

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: Any

class ChatRequest(BaseModel):
    session_id: Optional[int]
    message: str

class ChatResponse(BaseModel):
    reply: ChatMessage
    stage: Optional[str]
    product: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    result :Optional[Any] = None
    recommend_models: Optional[Any] = None
    session_id: Optional[Any] = None