from sqlalchemy.orm import Session
from app.db.models.user_session import UserSession
from app.schemas.user_session import UserSessionCreate
from app.core.session_manager import use_db

class UserSessionRepository:

    @use_db
    def create(payload: UserSessionCreate, db: Session) -> UserSession:
        session = UserSession(
            u_id=payload.u_id,
            refresh_token=payload.refresh_token,
            expires_at=payload.expires_at,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @use_db
    def get_by_refresh_token(token: str, db: Session) -> UserSession | None:
        return db.query(UserSession).filter(UserSession.refresh_token == token).first()
