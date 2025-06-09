from fastapi import FastAPI
from src.app.api.v1.endpoints import chat, documents, status
from src.app.utils.logging import init_logger

logger = init_logger()
logger.info("GenAI RAG System is starting...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="GenAI RAG Chatbot",
        description="Chatbot API using RAG architecture with FastAPI",
        version="1.0.0"
    )
    app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
    app.include_router(documents.router, prefix="/api/v1", tags=["Upload"])
    app.include_router(status.router, prefix="/api/v1", tags=["Status"])
    return app

app = create_app()
