from fastapi import Request, Header, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials
from app.utils.response_builder import ResponseBuilder
from app.modules.auth.jwt import decode_token
from app.api.security import bearer_scheme

PUBLIC_PATHS = (
    "/api/v1/auth",
    "/api/v1/health",
    "/docs",
)

class AuthDependency:

    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    ):
        if request.url.path.startswith(PUBLIC_PATHS):
            return

        if credentials is None:
            raise HTTPException(
                status_code=401,
                detail=ResponseBuilder.error(
                    message="Authorization header missing",
                    code=401
                ).dict()
            )

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=401,
                detail=ResponseBuilder.error(
                    message="Invalid authorization format",
                    code=401
                ).dict()
            )

        token = credentials.credentials  

        try:
            payload = decode_token(token)

            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=401,
                    detail=ResponseBuilder.error(
                        message="Invalid token type",
                        code=401
                    ).dict()
                )

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail=ResponseBuilder.error(
                        message="Invalid token payload",
                        code=401
                    ).dict()
                )

            request.state.user_id = user_id
            request.state.user = payload

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ResponseBuilder.error(
                    message=str(e),
                    code=401
                ).dict()
            )
