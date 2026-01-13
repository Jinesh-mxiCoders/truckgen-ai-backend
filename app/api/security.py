from fastapi.security import HTTPBearer, APIKeyHeader

bearer_scheme = HTTPBearer(
    scheme_name="Authorization",
    description="JWT Bearer token (Authorization: Bearer <token>)",
    auto_error=False
)

app_token_scheme = APIKeyHeader(
    name="app-token",
    scheme_name="AppToken",
    description="Application-level API token",
    auto_error=False
)
