from email.mime import text
from app.core.database import Database, Base
from sqlalchemy import text
from app.core.redis import Redis

db = Database()

def check_db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(Base.metadata.tables.keys())
        print("✅ Database connected successfully")
    except Exception as e:
        print("❌ Database connection failed:", e)

def is_redis_connected():
    """Check if Redis is connected"""
    try:
        redis_client = Redis().client
        res =redis_client.ping()
        print("✅ Redis connected successfully", res)
    except Exception as e:
        print(f"Redis connection error: {e}")
        return False
