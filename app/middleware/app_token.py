from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from config import settings
from app.utils.response_builder import ResponseBuilder


class AppTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("app_token")

        if not token or token != settings.APP_TOKEN:
            response_content = ResponseBuilder.error(
                message="Invalid or missing app_token",
                code=401
            ).dict()
            return JSONResponse(status_code=401, content=response_content)

        response = await call_next(request)
        return response
