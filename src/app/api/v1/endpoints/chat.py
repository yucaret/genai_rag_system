from pydantic import BaseModel
from src.app.domain.chat.services import ChatService
from fastapi import APIRouter
from src.app.domain.chat.services import ChatService

router = APIRouter()
chat_service = ChatService()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Remove the use_llm_fallback parameter if not needed
    print("chat.py --> def chat --> mensaje recibido desde frontend: " + str(request.message))
    return chat_service.get_response(request.message)
