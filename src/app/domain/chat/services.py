from src.app.infrastructure.llm.rag_chain_instance import rag_chain
from datetime import datetime, timezone

class ChatService:
    def get_response(self, user_input: str) -> dict:
        answer = rag_chain.run(user_input)
        return {
            "response": answer,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
