from src.app.infrastructure.llm.chains import RAGChain

# Agrega: se crea una real carpeta para guardar el vector store, 17-06-2025
os.makedirs("vector_db", exist_ok=True)

# SINGLETON that will persist through app
# Cambia: se cambia a la carpeta vector_db
#rag_chain = RAGChain(persistence_dir="vector_store")
rag_chain = RAGChain(persistence_dir="vector_db")