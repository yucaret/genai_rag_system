from fastapi import APIRouter
from src.app.infrastructure.llm.rag_chain_instance import rag_chain

router = APIRouter()

@router.get("/vector-status")
def status():
    return {"chunks": rag_chain.vector_store.index.ntotal}
