#import openai
#from config.settings import settings
#
#class OpenAIProvider:
#    def __init__(self):
#        openai.api_key = settings.openai_api_key
#        self.model = settings.openai_model
#
#    def chat_completion(self, prompt: str) -> str:
#        response = openai.ChatCompletion.create(
#            model=self.model,
#            messages=[{"role": "user", "content": prompt}]
#        )
#        return response.choices[0].message["content"]
        
from langchain_openai import ChatOpenAI
from config.settings import settings
## agregar 24-06-2025: libreria de memoria
from src.app.utils.memory import save_message, get_history, DEFAULT_CHAT_ID

class OpenAIProvider:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,  # ej. "gpt-3.5-turbo"
            api_key=settings.openai_api_key,
            temperature=0.0
        )

    # modificado 24-06-2025
    #def chat_completion(self, prompt: str) -> str:
    #    response = self.llm.invoke(prompt)
    #    return response.content
    def chat_completion(self, prompt: str) -> str:
        # 1. Obtener historial de mensajes pasados
        messages = get_history(DEFAULT_CHAT_ID)
        
        # 2. Agregar el nuevo mensaje del usuario
        messages.append({"role": "user", "content": prompt})
        
        # 3. Llamar al LLM con el historial completo
        response = self.llm.invoke(messages)
        
        # 4. Guardar el mensaje del usuario y la respuesta
        print("providers.py --> Clases OpenAIProvider --> chat_completion")
        save_message("user", prompt, DEFAULT_CHAT_ID)
        save_message("assistant", response.content, DEFAULT_CHAT_ID)
        
        return response.content