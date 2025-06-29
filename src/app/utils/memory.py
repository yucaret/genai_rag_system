import redis
import os
import json

# Conexi�n Redis remota (Railway)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

DEFAULT_CHAT_ID = "default_user"
MAX_HISTORY = 20

def save_message(role: str, content: str, chat_id: str = DEFAULT_CHAT_ID):
    key = f"chat_memory:{chat_id}"
    history = get_history(chat_id)
    
    #print(f"memory.py --> [Redis] --> save_message --> Historia Anterior Guardada: {role} => {str(history)}")
    print(f"memory.py --> [Redis] --> save_message --> Historia Cantidad Anterior Guardada: {len(history)} mensajes")
    
    history.append({"role": role, "content": content})
    history = history[-MAX_HISTORY:]
    r.set(key, json.dumps(history))
    
    print(f"memory.py --> [Redis] --> save_message --> Agregado a Historial: {role} => {content}")

def get_history(chat_id: str = DEFAULT_CHAT_ID):
    key = f"chat_memory:{chat_id}"
    data = r.get(key)
    
    print(f"memory.py --> [Redis] --> get_history --> Cargando historial para: {chat_id}")
    
    if data:
        history = json.loads(data)
        #print(f"memory.py --> [Redis] --> get_history --> Historial Encontrado: {str(history)}")
        print(f"memory.py --> [Redis] --> get_history --> Historial Cantidad Encontrada: {len(history)} mensajes")
        
        return history
    
    print("memory.py --> [Redis] --> get_history --> No hay historial previo.")
    
    return []

def reset_history(chat_id: str = DEFAULT_CHAT_ID):
    r.delete(f"chat_memory:{chat_id}")