from datetime import datetime, timezone
from fastapi import HTTPException
from app.schemas.user import UserCreate, UserLogin
from app.schemas.user_session import UserSessionCreate
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.user_session_repo import UserSessionRepository
from app.modules.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.modules.auth.security import (
    hash_password,
    verify_password
)

class AuthService:

    @staticmethod
    async def register(payload: UserCreate):
        existing = UserRepository.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists"
            )
        
        password_hash = hash_password(payload.password)
        user = UserRepository.create(payload, password_hash)
        return {
            "u_id": user.u_id,
            "name":user.name,
            "email":user.email
        }

    @staticmethod
    async def login(payload: UserLogin):
        user = UserRepository.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Ivalid credentials"
            )

        access_token, access_exp = create_access_token(str(user.u_id))
        refresh_token, refresh_exp = create_refresh_token(str(user.u_id))

        session_payload = UserSessionCreate(
            u_id=user.u_id,
            refresh_token=refresh_token,
            expires_at=refresh_exp,
        )
        UserSessionRepository.create(session_payload)

        return {
            "access_token": access_token,
            "access_token_expires_at": access_exp,
            "refresh_token": refresh_token,
            "refresh_token_expires_at": refresh_exp,
            "token_type": "Bearer",
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail=str(e)
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )

        session = UserSessionRepository.get_by_refresh_token(refresh_token)
        if not session or session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401,
                detail="Refresh token expired or invalid"
            )

        access_token, access_exp = create_access_token(str(user_id))

        return {
            "access_token": access_token,
            "access_token_expires_at": access_exp,
            "token_type": "Bearer",
        }