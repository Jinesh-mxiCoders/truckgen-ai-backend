from pydantic import BaseModel
from datetime import datetime

class UserSessionBase(BaseModel):
    u_id: int
    refresh_token: str
    expires_at: datetime

class UserSessionCreate(UserSessionBase):
    pass
