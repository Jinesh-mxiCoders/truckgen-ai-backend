from fastapi import HTTPException
from app.db.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse

class UserService:

    async def get_user_profile(self, user_id: int) -> UserResponse | None:
        user = UserRepository.get_by_id(u_id=user_id)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return UserResponse(
            u_id=user.u_id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
