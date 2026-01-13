from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    role: str | None = "user"
    is_active: bool | None = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    u_id: int
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
