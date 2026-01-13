from fastapi import Request, Header, HTTPException, Security
from config import settings
from app.utils.response_builder import ResponseBuilder
from app.api.security import app_token_scheme

class AppTokenDependency:
    def __init__(self):
        self.valid_token = settings.APP_TOKEN

    async def __call__(
        self,
        request: Request,
        app_token: str | None = Security(app_token_scheme),
    ):
        if request.url.path.startswith(("/api/v1/health", "/static")):
            return
        
        if not app_token:
            raise HTTPException(
                status_code=401,
                detail=ResponseBuilder.error(
                    message="Token in header is required",
                    code=401
                ).dict()
            )

        if app_token != self.valid_token:
            raise HTTPException(
                status_code=401,
                detail=ResponseBuilder.error(
                    message="Invalid Token",
                    code=401
                ).dict()
            )