from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1.endpoints import chat, documents, status, graph
from src.app.utils.logging import init_logger
##
from importlib.metadata import version, PackageNotFoundError
##

logger = init_logger()
logger.info("GenAI RAG System is starting...")

##
def log_package_versions():
    packages = ["openai", "langchain", "langchain-openai", "langchain-community"]
    for pkg in packages:
        try:
            v = version(pkg)
            logger.info(f"{pkg} version: {v}")
        except PackageNotFoundError:
            logger.warning(f"{pkg} is not installed.")

log_package_versions()
##

def create_app() -> FastAPI:
    app = FastAPI(
        title="GenAI RAG Chatbot",
        description="Chatbot API using RAG architecture with FastAPI",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace with your frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    
    app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
    app.include_router(documents.router, prefix="/api/v1", tags=["Upload"])
    app.include_router(status.router, prefix="/api/v1", tags=["Status"])
    app.include_router(graph.router, prefix="/api/v1", tags=["Graph"])
    return app

app = create_app()
