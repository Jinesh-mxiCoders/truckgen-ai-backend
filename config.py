from pydantic_settings import BaseSettings
from typing import ClassVar
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    DATABASE_URL: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    OPENAI_EMBEDDING_MODEL : str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    APP_TOKEN: str
    BASE_URL: str

    class Config:
        env_file = ".env"

settings =Settings()