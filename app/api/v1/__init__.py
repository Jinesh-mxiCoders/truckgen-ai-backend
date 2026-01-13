from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .chat import router as chat_router
from .ingest_json import router as ingest_json_router

api_v1_router = APIRouter()
print("api_v1_router", api_v1_router)
routers = [
    (auth_router, "/auth"),
    (user_router, "/user"),
    (chat_router, "/chat"),
    (ingest_json_router, "/ingest"),
]

for router, prefix in routers:
    api_v1_router.include_router(router, prefix=prefix)
