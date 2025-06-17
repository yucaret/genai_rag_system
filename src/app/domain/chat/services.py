from src.app.infrastructure.llm.rag_chain_instance import run_rag_with_langgraph
from src.app.infrastructure.llm.providers import OpenAIProvider
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.llm = OpenAIProvider()

    def get_response(self, user_input: str) -> dict:
        try:
            # Try RAG first
            result = run_rag_with_langgraph(user_input)
            
            # If RAG found results
            if result['doc_id'] not in ['none', 'error']:
                return {
                    "response": f"{result['answer']} (📄 Fuente: {result['doc_id']})",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Fallback to LLM
            llm_response = self.llm.chat_completion(
                f"El usuario preguntó: '{user_input}'. "
                "Responde de manera amable y útil como un asistente AI."
            )
            
            return {
                "response": llm_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            return {
                "response": "Disculpa, estoy teniendo dificultades técnicas. ¿Podrías reformular tu pregunta?",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }




# from src.app.infrastructure.llm.rag_chain_instance import rag_chain
# from src.app.infrastructure.llm.rag_chain_instance import run_rag_with_langgraph
# from datetime import datetime, timezone
# 
# class ChatService:
#     def get_response(self, user_input: str) -> dict:
#         result = run_rag_with_langgraph(user_input)
#         return {
#             "response": f"{result['answer']} (📄 Fuente: {result['doc_id']})",
#             "timestamp": datetime.now(timezone.utc).isoformat()
#         }
# 