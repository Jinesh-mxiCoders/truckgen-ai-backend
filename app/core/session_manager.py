from functools import wraps
from app.core.database import db_instance

def use_db(func):
    """
    Decorator to automatically provide a SQLAlchemy session to the function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_instance.get_session() as db:
            return func(*args, db=db, **kwargs)
    return wrapper
