#import openai
#import hashlib
#from src.app.infrastructure.cache.redis import RedisCache
#
#class EmbeddingAdapter:
#    def __init__(self, model="text-embedding-3-small"):
#        self.model = model
#        self.embedding_dim = 1536
#        self.cache = RedisCache()
#        
#    def _hash(self, text: str) -> str:
#        return f"embedding:{self.model}:{hashlib.sha256(text.encode()).hexdigest()}"
#
#    def get_embedding(self, text: str) -> list[float]:
#        cache_key = self._hash(text)
#        cached = self.cache.get(cache_key)
#        if cached:
#            return cached
#
#        response = openai.Embedding.create(model=self.model, input=text)
#        embedding = response['data'][0]['embedding']
#        self.cache.set(cache_key, embedding)
#        return embedding
#
#    def embed(self, texts: list[str]) -> list[list[float]]:
#        result = []
#        uncached = []
#        uncached_texts = []
#
#        for text in texts:
#            cache_key = self._hash(text)
#            cached = self.cache.get(cache_key)
#            if cached:
#                result.append(cached)
#            else:
#                uncached.append(cache_key)
#                uncached_texts.append(text)
#
#        if uncached_texts:
#            response = openai.Embedding.create(model=self.model, input=uncached_texts)
#            for key, r in zip(uncached, response['data']):
#                self.cache.set(key, r["embedding"])
#                result.append(r["embedding"])
#
#        return result

import hashlib
from langchain_openai import OpenAIEmbeddings
from config.settings import settings
from src.app.infrastructure.cache.redis import RedisCache

class EmbeddingAdapter:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.cache = RedisCache()

        self.embedder = OpenAIEmbeddings(
            model=self.model,
            api_key=settings.openai_api_key        # tomado del .env / variable de entorno
        )

        self.embedding_dim = self.embedder.embed_query("test").__len__()

    def _hash(self, text: str) -> str:
        return f"embedding:{self.model}:{hashlib.sha256(text.encode()).hexdigest()}"

    def get_embedding(self, text: str) -> list[float]:
        cache_key = self._hash(text)
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        embedding = self.embedder.embed_query(text)
        self.cache.set(cache_key, embedding)
        return embedding

    def embed(self, texts: list[str]) -> list[list[float]]:
        result: list[list[float]] = []
        to_embed: list[str] = []
        pending_keys: list[str] = []

        for t in texts:
            k = self._hash(t)
            cached = self.cache.get(k)
            if cached:
                result.append(cached)
            else:
                pending_keys.append(k)
                to_embed.append(t)

        if to_embed:
            embeddings = self.embedder.embed_documents(to_embed)
            for k, emb in zip(pending_keys, embeddings):
                self.cache.set(k, emb)
                result.append(emb)

        return result