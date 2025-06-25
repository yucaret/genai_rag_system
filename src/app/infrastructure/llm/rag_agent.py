from langchain.agents import initialize_agent, AgentType
from src.app.infrastructure.tools import TOOLS
from config.settings import settings
from src.app.infrastructure.vector_store.faiss import FaissStore
from src.app.infrastructure.llm.adapters import EmbeddingAdapter
import numpy as np

# Modificar 24-06-2025: Modificar librerias
#from langchain.chat_models import ChatOpenAI
from src.app.infrastructure.llm.providers import OpenAIProvider
##

# Agregar 24-06-2025: save_message
from src.app.utils.memory import save_message
##

class RAGAgent:
    def __init__(self, vector_dir="vector_db"):
        self.embedder = EmbeddingAdapter()
        self.vector_store = FaissStore(self.embedder, persistence_dir=vector_dir)
        
        # Modificar 24-06-2025: Modificar llm
        #self.llm = ChatOpenAI(
        #        model=settings.openai_model,  # Ej: "gpt-3.5-turbo"
        #        temperature=0,
        #        openai_api_key=settings.openai_api_key
        #)
        self.llm = OpenAIProvider()
        ##
        
        # Modificar 24-06-2025: Modificar initialize_agent
        #self.agent = initialize_agent(
        #    tools=TOOLS,
        #    llm=self.llm,
        #    agent=AgentType.OPENAI_FUNCTIONS,
        #    verbose=True,
        #)
        self.agent = initialize_agent(
            tools=TOOLS,
            llm=self.llm.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
        )
        ##

    def run(self, question: str) -> str:
        # 1) Pregunta directo al agente.  Si él necesita la vector-db, la tool, etc.
        try:
            print("rag_agent.py --> class RAGAgent --> def run")
            
            # Agregar 24-06-2025: obtener historia y agregar la nueva consulta
            history = get_history(DEFAULT_CHAT_ID)
            history.append({"role": "user", "content": question})
            ##
            
            # Modificar 24-06-2025: 
            #answer = self.agent.run(question)
            response = self.agent.invoke(history)
            answer = response["output"]
            
            # Agregar 24-06-2025: save_message user y assistant
            save_message("user", question)
            save_message("assistant", answer)
            ##
            
            return answer
            
        except Exception as e:
            # 2) fallback manual a búsqueda vectorial (opcional)
            print(f"ERROR rag_agent.py --> Clases RAGAgent --> run: {e}")
            q_emb = np.array([self.embedder.get_embedding(question)], dtype=np.float32)
            docs = self.vector_store.search(q_emb, top_k=5)
            context = "\n".join(d["text"] for d in docs)
            prompt = f"Contexto:\n{context}\n\nPregunta: {question}\nRespuesta:"
            
            return OpenAIProvider().chat_completion(prompt)