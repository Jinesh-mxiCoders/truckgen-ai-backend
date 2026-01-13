from fastapi import APIRouter, Depends, HTTPException
from app.modules.auth.service import AuthService
from app.schemas.user import UserCreate, UserLogin
from app.schemas.user_session import UserSessionBase
from app.utils.response_builder import ResponseBuilder
from app.schemas.api_response import APIResponse
from app.core.database import Database

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=APIResponse)
async def register(payload: UserCreate):
    try:
        data = await AuthService.register(payload)
        return ResponseBuilder.success(data, "User registered Successfully")
    
    except HTTPException as e:
        return ResponseBuilder.error(
            message=e.detail,
            code=e.status_code
        )


@router.post("/login", response_model=APIResponse)
async def login(payload: UserLogin):
    try:
        data = await AuthService.login(payload)
        return ResponseBuilder.success(data, "User Loogedin successfully")
    
    except HTTPException as e:
        return ResponseBuilder.error(
            message=e.detail,
            code=e.status_code
        )

@router.post("/refresh-token", response_model=APIResponse)
async def refresh_token(payload: dict):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        return ResponseBuilder.error(message="Refresh token is required", code=401)

    try:
        data = await AuthService.refresh_access_token(refresh_token)
        return ResponseBuilder.success(data, "Access token refreshed successfully")
    except HTTPException as e:
        return ResponseBuilder.error(
            message=e.detail,
            code=e.status_code
        )