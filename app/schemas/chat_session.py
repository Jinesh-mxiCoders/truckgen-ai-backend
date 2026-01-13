from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatSessionBase(BaseModel):
    u_id: int
    cb_id: int
    redis_key: str
    status: Optional[str] = "active"

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    ch_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
