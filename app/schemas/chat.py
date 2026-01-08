from pydantic import BaseModel
from typing import Dict, Any, Optional, Literal

class MessageContent(BaseModel):
    text: Optional[str] = None
    image: Optional[list[str]] = None
    data: Optional[dict] = None

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: MessageContent

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: Any
    # completed: Optional[bool]
    stage: Optional[str]
    product: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    result :Optional[Any] = None
    recommend_models: Optional[Any] = None