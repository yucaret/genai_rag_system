from langchaiTOOLSn.agents import initialize_agent, AgentType
from src.app.infrastructure.tools import TOOLS
from src.app.infrastructure.llm.providers import OpenAIProvider
from src.app.infrastructure.vector_store.faiss import FaissStore
from src.app.infrastructure.llm.adapters import EmbeddingAdapter
import numpy as np

class RAGAgent:
    def __init__(self, vector_dir="vector_db"):
        self.embedder = EmbeddingAdapter()
        self.vector_store = FaissStore(self.embedder, persistence_dir=vector_dir)
        self.llm = OpenAIProvider().llm  # <<— obtenemos ChatOpenAI listo

        self.agent = initialize_agent(
            tools=TOOLS,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
        )

    def run(self, question: str) -> str:
        # 1) Pregunta directo al agente.  Si él necesita la vector-db, la tool, etc.
        try:
            answer = self.agent.run(question)
            return answer
        except Exception:
            # 2) fallback manual a búsqueda vectorial (opcional)
            q_emb = np.array([self.embedder.get_embedding(question)], dtype=np.float32)
            docs = self.vector_store.search(q_emb, top_k=5)
            context = "\n".join(d["text"] for d in docs)
            prompt = f"Contexto:\n{context}\n\nPregunta: {question}\nRespuesta:"
            return OpenAIProvider().chat_completion(prompt)
