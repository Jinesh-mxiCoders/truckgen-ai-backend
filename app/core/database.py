from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager
from config import settings

class Database:
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.engine = self._create_engine()
        self.SessionLocal = self._create_sessionmaker()

    def _create_engine(self):
        return create_engine(
            self.database_url,
            future=True,
            pool_pre_ping=True
        )

    def _create_sessionmaker(self):
        return sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False
        )

    @contextmanager
    def get_session(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


class Base(DeclarativeBase):
    pass

db_instance = Database()