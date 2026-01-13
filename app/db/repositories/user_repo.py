from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.core.session_manager import use_db

class UserRepository:
    
    @staticmethod
    @use_db
    def get_by_email(email: str, db: Session, ) -> User | None:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    @use_db
    def get_by_id(u_id: int, db: Session) -> User | None:
        return db.query(User).filter(User.u_id == u_id, User.is_active == True).first()

    @staticmethod
    @use_db
    def create(payload: UserCreate, password: str, db: Session, ) -> User:
        user = User(
            email=payload.email,
            name=payload.name,
            role=payload.role,
            is_active=payload.is_active,
            password=password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
