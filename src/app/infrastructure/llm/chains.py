import numpy as np
from textwrap import wrap
import tiktoken
from typing import List
from src.app.infrastructure.llm.adapters import EmbeddingAdapter
from src.app.infrastructure.vector_store.faiss import FaissStore
from src.app.infrastructure.llm.providers import OpenAIProvider
import hashlib
from src.app.infrastructure.cache.redis import redis_client
import logging
logger = logging.getLogger("genai")

class RAGChain:
    def __init__(self):
        self.embedder = EmbeddingAdapter()
        self.vector_store = FaissStore(embedder=self.embedder)
        self.llm = OpenAIProvider()

    def ingest_document(self, text: str):
        chunks = self.split_text(text)
        logger.info(f"Total chunks created: {len(chunks)}")
        self.vector_store.add_documents(chunks) 
    
    def split_text(self, text: str, max_tokens: int = 200) -> List[str]:
        encoding = tiktoken.encoding_for_model("text-embedding-3-small")
        tokens = encoding.encode(text)

        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk = tokens[i:i+max_tokens]
            chunks.append(encoding.decode(chunk))

        logger.info(f"Token-split into {len(chunks)} chunks.")
        return chunks
    
    def run(self, query: str) -> str:
        query_embedding = self.embedder.get_embedding(query)
        query_embedding_np = np.array([query_embedding], dtype=np.float32)

        query_hash = hashlib.sha256(query.encode()).hexdigest()
        cache_key = f"context:{query_hash}"
        
        cached_chunks = redis_client.get(cache_key)
        if cached_chunks:
            context_chunks = cached_chunks 
            logger.info("Cache hit")
        else:
           
            context_chunks = self.vector_store.search(query_embedding_np)
            redis_client.set(cache_key, context_chunks, expire_seconds=3600)
            logger.info("VectorDB hit")

        context = "\n".join(context_chunks)
        prompt = (
            f"Utiliza el siguiente contexto para responder la pregunta en español:\n\n"
            f"{context}\n\n"
            f"Pregunta: {query}\nRespuesta:"
        )
        return self.llm.chat_completion(prompt)
    


