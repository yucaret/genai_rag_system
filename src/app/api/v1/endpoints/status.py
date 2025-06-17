# src/app/api/v1/endpoints/status.py
from fastapi import APIRouter
from src.app.infrastructure.llm.rag_container import rag_chain  # ← USE THIS

router = APIRouter()

@router.get("/vector-status")
def status():
    return {
        "document_count": len(rag_chain.vector_store.documents),
        "index_trained": rag_chain.vector_store.is_trained,
        "ready": len(rag_chain.vector_store.documents) > 0
    }
