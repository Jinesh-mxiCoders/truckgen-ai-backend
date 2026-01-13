from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.response_builder import ResponseBuilder

async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseBuilder.error(
            message=str(exc.detail),
            code=exc.status_code
        ).dict()
    )
