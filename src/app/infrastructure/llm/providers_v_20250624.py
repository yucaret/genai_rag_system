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

class OpenAIProvider:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,  # ej. "gpt-3.5-turbo"
            api_key=settings.openai_api_key,
            temperature=0.0
        )

    def chat_completion(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return response.content