from fastapi import APIRouter, Depends, Request, HTTPException
from app.modules.user.user_service import UserService
from app.utils.response_builder import ResponseBuilder

router = APIRouter(tags=["User"])

@router.get("/profile")
async def get_user_profile(req: Request):
    try:
        user_id = int(req.state.user_id)
        user_profile = await UserService().get_user_profile(user_id)
        return ResponseBuilder.success(user_profile, "User profile fetched successfully")

    except Exception as e:
        return ResponseBuilder.error(
            message=e.detail,
            code=e.status_code
        )
