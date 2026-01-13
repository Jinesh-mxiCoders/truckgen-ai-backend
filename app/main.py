from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.startup import check_db_connection, is_redis_connected
from app.rag.vectorstore import vector_store
from app.middleware.app_token import AppTokenDependency
from app.modules.auth.middleware import AuthDependency
from app.handlers.exception_handlers import http_exception_handler
from app.api.v1 import api_v1_router

app = FastAPI(
    title="TuckGen AI ", 
    version="0.1.0",
    dependencies=[
        Depends(AppTokenDependency()),
        Depends(AuthDependency())
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


@app.on_event("startup")
def startup():
    check_db_connection()
    is_redis_connected()
    vector_store.init_pgvector()

app.include_router(api_v1_router, prefix="/api/v1")