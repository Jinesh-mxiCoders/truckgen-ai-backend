from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from app.enums.chat import ChatRoleEnum

class ChatMessageBase(BaseModel):
    cs_id: int
    role: ChatRoleEnum
    content: Dict[str, Any]

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    cm_id: int
    created_at: datetime

    class Config:
        from_attributes = True
