from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.startup import check_db_connection, is_redis_connected
from app.rag.vectorstore import vector_store
from app.api.v1.chat import router as chat_router
from app.api.v1.ingest_json import router as ingest_json_router
from fastapi.staticfiles import StaticFiles
from app.middleware.app_token import AppTokenMiddleware

app = FastAPI(title="TuckGen AI ", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AppTokenMiddleware)

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

app.include_router(chat_router, prefix="/api/v1")
app.include_router(ingest_json_router, prefix="/api/v1")
