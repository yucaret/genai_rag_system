import redis
import json
import os
import pickle
from typing import Any, Optional

class RedisCache:
#    def __init__(self):
#        redis_host = os.getenv("REDIS_HOST", "localhost")
#        redis_port = int(os.getenv("REDIS_PORT", "6379"))
#
#        self.client = redis.Redis(host=redis_host, port=redis_port, db=0)

# Para api publica
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            self.client = redis.from_url(redis_url#,
            #decode_responses=True
            )
        else:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0))#,
                #decode_responses=True
            )

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        pickled = pickle.dumps(value)
        self.client.set(key, pickled, ex=ex)

    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        if value is None:
            return None

        try:
            return pickle.loads(value)
        except (pickle.UnpicklingError, TypeError):
            try:
                return json.loads(value)
            except Exception:
                return None

        
redis_client = RedisCache()