import redis
from config import settings

class Redis:
    def __init__(self):
        self._client = None

    def connect(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        return self._client

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            return self.connect()
        return self._client
    
redis_client = Redis().client