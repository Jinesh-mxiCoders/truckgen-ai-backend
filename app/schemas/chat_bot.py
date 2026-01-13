from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class ChatBotBase(BaseModel):
    name: str
    description: Optional[str] = None

class ChatBotCreate(ChatBotBase):
    pass

class ChatBotResponse(ChatBotBase):
    cb_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
