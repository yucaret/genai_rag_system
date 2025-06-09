import faiss
import numpy as np
from typing import List
import logging
logger = logging.getLogger("genai")

class FaissStore:
    def __init__(self, embedder=None, dim: int = 1536):
        self.embedder = embedder
        self.dim = embedder.embedding_dim if embedder else dim
        self.index = faiss.IndexFlatL2(self.dim)
        self.documents = []

    def add_documents(self, texts: List[str]):
        if not texts:
            return

        if not self.embedder:
            raise ValueError("No embedder set. Cannot generate embeddings.")

        embeddings = self.embedder.embed(texts)
        self.index.add(np.array(embeddings).astype(np.float32))
        self.documents.extend(texts)

        logger.info(f"Added {len(texts)} chunks. Total in index: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            logger.info("Vector store is empty.")
            return ["No documents available. Please upload PDF first."]

        if query_embedding.shape != (1, self.dim):
            raise ValueError(f"Query embedding must have shape (1, {self.dim}). Got: {query_embedding.shape}")

        _, indices = self.index.search(query_embedding, top_k)

        results = []
        for i in indices[0]:
            if i < len(self.documents):
                results.append(self.documents[i])
            else:
                results.append(f"[Missing chunk {i}]")

        return results
