from passlib.hash import bcrypt
from datetime import datetime, timedelta
from config import Settings
import secrets

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)

def refresh_token_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=Settings.REFRESH_TOKEN_EXPIRE_DAYS)
