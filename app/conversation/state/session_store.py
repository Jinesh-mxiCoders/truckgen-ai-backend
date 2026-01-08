import json
from app.core.redis import redis_client

class SessionStore:
    """Class to manage conversation session data in Redis."""

    def __init__(self):
        self.redis_client = redis_client

    def get_session(self, session_id: str) -> dict:
        data = self.redis_client.get(session_id)
        if data:
            return json.loads(data)

        session = {
            "stage": "welcome",
            "product": None,
            "data": {},
            "current_field": None,
            "recommend_models": [], 
            "models": [],
            "selected_models":None,
            "messages": [],
            "completed": False,
            "rag_validated": False,
            "errors": []
        }
        self.redis_client.set(session_id, json.dumps(session))
        return session

    def update_session(self, session_id: str, session_data: dict):
        self.redis_client.set(session_id, json.dumps(session_data))

    def delete_session(self, session_id: str):
        self.redis_client.delete(session_id)
