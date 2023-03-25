import json
from abc import ABC, abstractmethod

from redis import Redis

from core.config import settings


class CacheStorage(ABC):
    @abstractmethod
    def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    def set(self, key: str, value: str, ex: int, **kwargs):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass


class RedisStorage(CacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    def get(self, key: str, **kwargs):
        data = self.redis.get(key)
        if data is None:
            return
        else:
            return json.loads(data)

    def set(self, key: str, value: str, ex: int, **kwargs):
        self.redis.set(key, json.dumps(value), ex)

    def delete(self, key: str, **kwargs):
        self.redis.delete(key)


redis = Redis(host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True)
redis_db = RedisStorage(redis)
