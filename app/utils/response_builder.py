from app.schemas.api_response import APIResponse


class ResponseBuilder:
    @staticmethod
    def success(data, message: str = "OK", code: int = 200) -> APIResponse:
        return APIResponse(
            status="success",
            status_code=code,
            message=message,
            data=data
        )

    @staticmethod
    def error(message: str, code: int = 400) -> APIResponse:
        return APIResponse(
            status="error",
            status_code=code,
            message=message,
            data=None
        )
