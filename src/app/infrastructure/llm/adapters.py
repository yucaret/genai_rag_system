import openai
import hashlib
from src.app.infrastructure.cache.redis import RedisCache


class EmbeddingAdapter:
    def __init__(self, model="text-embedding-3-small"):
        self.model = model
        self.embedding_dim = 1536
        self.cache = RedisCache()
        
    def _hash(self, text: str) -> str:
        return f"embedding:{self.model}:{hashlib.sha256(text.encode()).hexdigest()}"

    def get_embedding(self, text: str) -> list[float]:
        cache_key = self._hash(text)
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        response = openai.Embedding.create(model=self.model, input=text)
        embedding = response['data'][0]['embedding']
        self.cache.set(cache_key, embedding)
        return embedding

    def embed(self, texts: list[str]) -> list[list[float]]:
        result = []
        uncached = []
        uncached_texts = []

        for text in texts:
            cache_key = self._hash(text)
            cached = self.cache.get(cache_key)
            if cached:
                result.append(cached)
            else:
                uncached.append(cache_key)
                uncached_texts.append(text)

        if uncached_texts:
            response = openai.Embedding.create(model=self.model, input=uncached_texts)
            for key, r in zip(uncached, response['data']):
                self.cache.set(key, r["embedding"])
                result.append(r["embedding"])

        return result

