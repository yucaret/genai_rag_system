import faiss
import pickle
import os
import numpy as np
from typing import List, Dict, Optional, Any
import logging
logger = logging.getLogger("genai")

class FaissStore:
    def __init__(self, embedder, dimension: int = None, persistence_dir: str = "vector_store"):
        logger.warning("🧠 FaissStore __init__ triggered")
        self.embedder = embedder
        self.persistence_dir = persistence_dir
        os.makedirs(self.persistence_dir, exist_ok=True)
        
        # Get embedding dimension from model if not provided
        self.dimension = dimension or self._get_embedding_dimension()
        
        # Initialize empty structures
        self.index = None
        self.documents = []
        self.is_trained = False
        
        # Try to load existing data
        self._load_persisted_data()
        
        # Create new index if none loaded
        if self.index is None:
            self._create_new_index()

    def _get_embedding_dimension(self) -> int:
        """Get embedding dimension from the embedder"""
        test_embedding = self.embedder.get_embedding("test")
        return len(test_embedding)

    def _create_new_index(self):
        """Initialize a new FAISS index with correct dimension"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.is_trained = False
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def _persist_data(self):
        """Persist both FAISS index and documents to disk"""
        index_path = os.path.join(self.persistence_dir, "faiss_index.bin")
        docs_path = os.path.join(self.persistence_dir, "documents.pkl")

        faiss.write_index(self.index, index_path)

        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)

        logger.info(f"Persisted FAISS index and {len(self.documents)} documents to disk")

    def _load_persisted_data(self):
        """Load both FAISS index and documents"""
        logger.warning("📦 Loading documents from disk...")
        index_path = os.path.join(self.persistence_dir, "faiss_index.bin")
        docs_path = os.path.join(self.persistence_dir, "documents.pkl")

        if os.path.exists(index_path):
            try:
                self.index = faiss.read_index(index_path)
                self.dimension = self.index.d
                self.is_trained = True
                logger.info(f"Loaded FAISS index with dimension {self.dimension}")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")

        if os.path.exists(docs_path):
            try:
                with open(docs_path, "rb") as f:
                    self.documents = pickle.load(f)
                logger.info(f"Loaded {len(self.documents)} document metadata records")
            except Exception as e:
                logger.error(f"Failed to load documents metadata: {e}")

        # Dimension consistency check
        if self.index and self.documents:
            test_embedding = self.embedder.get_embedding("test")
            if len(test_embedding) != self.dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: index={self.dimension}, embedder={len(test_embedding)}"
                )

    def add_documents(self, texts: List[str], metadata: Optional[Dict] = None):
        """Safe document addition with dimension validation"""
        if not texts:
            raise ValueError("Cannot add empty list of texts")
        
        # Generate embeddings with validation
        embeddings = []
        for text in texts:
            embedding = np.array(self.embedder.get_embedding(text), dtype=np.float32)
            if len(embedding) != self.dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: "
                    f"expected {self.dimension}, got {len(embedding)}"
                )
            embeddings.append(embedding)
        
        embeddings = np.array(embeddings)
        
        # Add to index
        if not self.is_trained and len(self.documents) > 0:
            self.index.train(embeddings)
            self.is_trained = True
        
        self.index.add(embeddings)
        
        # Store documents metadata
        default_meta = metadata or {}
        new_docs = [
            {"text": text, "metadata": {**default_meta, "chunk_id": len(self.documents) + i}}
            for i, text in enumerate(texts)
        ]
        self.documents.extend(new_docs)
        self._persist_data()
        logger.info(f"Added {len(texts)} documents (total: {len(self.documents)})")

    def search(self, query_embedding, top_k=5):
        if not self.documents:
            logger.error("Vector store is empty - no documents to search")
            return []
        
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        
        # modificado 2025-06-25: Se agrega el score
        #for idx in indices[0]:
        for i, idx in enumerate(indices[0]):
        ##
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
            try:
                # modificado 2025-06-25: Se agrega el score
                #results.append(self.documents[idx])
                
                doc = self.documents[idx].copy()
                doc["score"] = float(1 / (1 + distances[0][i]))  # el score inversamente proporcional a distancia
                results.append(doc)
                
                ##
            except IndexError:
                logger.warning(f"Invalid index {idx} returned from FAISS")
                continue
                
        return results

    def save_index(self, path: str):
        """Persist the FAISS index to disk"""
        faiss.write_index(self.index, path)
        logger.info(f"Saved FAISS index to {path}")

    def load_index(self, path: str):
        """Load a persisted FAISS index"""
        self.index = faiss.read_index(path)
        self.is_trained = True
        logger.info(f"Loaded FAISS index from {path}")
