from src.app.infrastructure.llm.chains import RAGChain

# SINGLETON that will persist through app
rag_chain = RAGChain(persistence_dir="vector_store")
