import redis
import json
import os

class RedisCache:

# Para localhost
#    def __init__(self):
#        self.redis = redis.Redis(
#            host=os.getenv("REDIS_HOST", "localhost"),
#            port=int(os.getenv("REDIS_PORT", 6379)),
#            db=int(os.getenv("REDIS_DB", 0)),
#            decode_responses=True
#        )

# Para api publica
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            self.redis = redis.from_url(redis_url, decode_responses=True)
        else:
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )

    def get(self, key: str):
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value, expire_seconds: int = 86400):
        self.redis.set(key, json.dumps(value), ex=expire_seconds)
        
redis_client = RedisCache()