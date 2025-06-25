import numpy as np
from textwrap import wrap
import tiktoken
from typing import Dict, List, Tuple
from src.app.infrastructure.llm.adapters import EmbeddingAdapter
from src.app.infrastructure.vector_store.faiss import FaissStore
from src.app.infrastructure.llm.providers import OpenAIProvider
import hashlib
from src.app.infrastructure.cache.redis import redis_client
from collections import defaultdict
import pickle  # Add this at the top of your chains.py file

## agregar 24-06-2025: libreria de memoria, save_message
from src.app.utils.memory import save_message


import logging
logger = logging.getLogger("genai")

class RAGChain:
    def __init__(self, persistence_dir: str = "vector_store"):
        self.embedder = EmbeddingAdapter()
        self.llm = OpenAIProvider()
        self.persistence_dir = persistence_dir
        
        # Initialize vector store with automatic recovery
        try:
            self.vector_store = FaissStore(
                embedder=self.embedder,
                persistence_dir=persistence_dir
            )
            self._verify_store()
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise

    def _verify_store(self):
        """Verify the store is in a valid state"""
        if not hasattr(self.vector_store, 'index') or self.vector_store.index is None:
            raise ValueError("FAISS index not initialized")
        
        test_embed = self.embedder.get_embedding("test")
        if len(test_embed) != self.vector_store.dimension:
            raise ValueError(
                f"Embedding dimension mismatch: "
                f"expected {self.vector_store.dimension}, got {len(test_embed)}"
            )

    def ingest_document(self, text: str, doc_id: str, section: str = "summary"):
        """Safe document ingestion"""
        if not text.strip():
            raise ValueError("Document text cannot be empty")
        if not doc_id.strip():
            raise ValueError("Document ID cannot be empty")
        
        chunks = self.split_text(text)
        if not chunks:
            raise ValueError("No valid chunks generated from document")
        
        try:
            self.vector_store.add_documents(
                texts=chunks,
                metadata={"section": section, "doc_id": doc_id}
            )
            logger.info(f"Successfully ingested document {doc_id}")
            
            from uuid import uuid4
            redis_client.set("vector_version", str(uuid4()))
            logger.info("Cache invalidated after ingestion")
        except Exception as e:
            logger.error(f"Failed to ingest document: {str(e)}")
            raise
    
    def split_text(self, text: str, max_tokens: int = 200) -> List[str]:
        encoding = tiktoken.encoding_for_model("text-embedding-3-small")
        tokens = encoding.encode(text)

        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk = tokens[i:i+max_tokens]
            chunks.append(encoding.decode(chunk))

        logger.info(f"Token-split into {len(chunks)} chunks.")
        return chunks
    
    def run(self, query: str, section: str = "all", use_cache: bool = True) -> dict:
        try:
            # Generate query embedding
            query_embedding = self.embedder.get_embedding(query)
            query_embedding_np = np.array([query_embedding], dtype=np.float32)

            # Cache versioning
            vector_version = redis_client.get("vector_version") or "v1"
            cache_key = hashlib.sha256(f"{query}:{section}:{vector_version}".encode()).hexdigest()
            redis_key = f"context:{cache_key}"

            # Try cache first
            if use_cache:
                cached = redis_client.get(redis_key)
                if cached:
                    try:
                        context_chunks, best_doc_id = pickle.loads(cached)
                        logger.info(f"Using cached results for: {query[:50]}...")
                        response = self._generate_response(context_chunks, best_doc_id, query)
                        return {
                            "answer": response["answer"],
                            "doc_id": response["doc_id"],
                            "source": "cache"
                        }
                    except Exception as e:
                        logger.warning(f"Cache read failed: {str(e)}")

            # Vector store search
            chunks = self.vector_store.search(query_embedding_np, top_k=50)
            processed_chunks = self._process_chunks(chunks, section)

            if processed_chunks:
                # Found in vector DB
                best_doc_id, context_chunks = self._rank_documents(processed_chunks)
                
                try:
                    redis_client.set(
                        redis_key,
                        pickle.dumps((context_chunks, best_doc_id)),
                        ex=3600
                    )
                except Exception as e:
                    logger.error(f"Caching failed: {str(e)}")

                response = self._generate_response(context_chunks, best_doc_id, query)
                return {
                    "answer": response["answer"],
                    "doc_id": response["doc_id"],
                    "source": "vector_db"
                }
            else:
                # Not found in vector DB - use LLM directly
                llm_response = self.llm.chat_completion(query)
                return {
                    "answer": llm_response,
                    "doc_id": "llm_fallback",
                    "source": "llm"
                }

        except Exception as e:
            logger.error(f"RAG error: {str(e)}", exc_info=True)
            # Fallback to LLM even in error cases
            llm_response = self.llm.chat_completion(query)
            return {
                "answer": llm_response,
                "doc_id": "llm_error_fallback",
                "source": "llm_error"
            }

    # def run(self, query: str, section: str = "all", use_cache: bool = True) -> dict:
    #     try:
    #         # Generate query embedding
    #         query_embedding = self.embedder.get_embedding(query)
    #         query_embedding_np = np.array([query_embedding], dtype=np.float32)
# 
    #         # Read vector index version
    #         vector_version = redis_client.get("vector_version")
    #         if vector_version is None:
    #             vector_version = "v1"  # Default version if not set
# 
    #         # Cache key includes version to ensure freshness after document ingestion
    #         cache_key = hashlib.sha256(f"{query}:{section}:{vector_version}".encode()).hexdigest()
    #         redis_key = f"context:{cache_key}"
# 
    #         # Try to load from cache
    #         if use_cache:
    #             cached = redis_client.get(redis_key)
    #             if cached:
    #                 try:
    #                     context_chunks, best_doc_id = pickle.loads(cached)
    #                     logger.info(f"Using cached results for query: {query}")
    #                     response = self._generate_response(context_chunks, best_doc_id, query)
    #                     return {
    #                         "answer": response["answer"],
    #                         "doc_id": response["doc_id"]
    #                     }
    #                 except pickle.PickleError as e:
    #                     logger.error(f"Error in RAG chain: {str(e)}", exc_info=True)
    #                     return {
    #                         "answer": "Ocurrió un error al procesar tu consulta",
    #                         "doc_id": "error"
    #                     }
# 
    #         # Vector store search
    #         chunks = self.vector_store.search(query_embedding_np, top_k=50)
# 
    #         # Process chunks into consistent format
    #         processed_chunks = self._process_chunks(chunks, section)
    #         if not processed_chunks:
    #             return {
    #                 "answer": "No encontré información relevante en los documentos",
    #                 "doc_id": "none"
    #             }
# 
    #         # Rank documents by chunk matches
    #         best_doc_id, context_chunks = self._rank_documents(processed_chunks)
# 
    #         # Cache results with versioned key
    #         try:
    #             redis_client.set(
    #                 redis_key,
    #                 pickle.dumps((context_chunks, best_doc_id)),
    #                 ex=3600
    #             )
    #         except (pickle.PickleError, TypeError) as e:
    #             logger.error(f"Failed to cache results: {str(e)}")
# 
    #         return self._generate_response(context_chunks, best_doc_id, query)
# 
    #     except Exception as e:
    #         logger.error(f"Error in RAG chain: {str(e)}", exc_info=True)
    #         return {
    #             "answer": "Ocurrió un error al procesar tu consulta",
    #             "doc_id": "error"
    #         }
# 
    def _process_chunks(self, chunks: List[Dict], section: str) -> List[Dict]:
        processed = []

        for chunk in chunks:
            # Case: FAISS returns just text
            if isinstance(chunk, str):
                processed.append({
                    "text": chunk,
                    "metadata": {"section": "unknown", "doc_id": "unknown"}
                })

            # Case: langchain.Document
            elif hasattr(chunk, "metadata"):
                processed.append({
                    "text": getattr(chunk, "page_content", ""),
                    "metadata": getattr(chunk, "metadata", {})
                })

            # Case: custom dict
            else:
                metadata = chunk.get("metadata", {})
                processed.append({
                    "text": chunk.get("text", ""),
                    "metadata": {
                        "section": metadata.get("section", "unknown"),
                        "doc_id": metadata.get("doc_id", "unknown"),
                        **metadata
                    }
                })

        if section != "all":
            processed = [
                c for c in processed if c["metadata"].get("section") == section
            ]

        return processed

    def _rank_documents(self, chunks: List[Dict]) -> Tuple[str, List[str]]:
        """
        Rank documents by cumulative similarity score of chunks.
        Returns: (best_doc_id, relevant_chunks_text_list)
        """
        doc_scores = defaultdict(float)
        doc_chunks = defaultdict(list)

        for chunk in chunks:
            meta = chunk.get("metadata", {})
            doc_id = meta.get("doc_id", "unknown")
            score = chunk.get("score", 0.0)  # <--- Important
            text = chunk.get("text", "")

            doc_scores[doc_id] += score
            doc_chunks[doc_id].append(text)

        if not doc_scores:
            return "none", []

        best_doc_id = max(doc_scores.items(), key=lambda x: x[1])[0]
        return best_doc_id, doc_chunks[best_doc_id]

    def _generate_response(self, context_chunks: List[str], doc_id: str, query: str) -> Dict[str, str]:
        """Generate LLM response from context."""
        context = "\n".join(context_chunks[:10])
        prompt = f"""Responde en español basándote en este contexto:
                Documento: {doc_id}
                Contexto: {context}

                Pregunta: {query}
                Respuesta:"""
        
        answer = self.llm.chat_completion(prompt)
        
        # agregar 24-06-2025: guarda la informacion de consulta y respuesta
        print("chains.py --> Clases RAGChain --> _generate_response")
        save_message("user", query)
        save_message("assistant", answer)
        ##
        
        return {
            "answer": answer,
            "doc_id": doc_id
        }