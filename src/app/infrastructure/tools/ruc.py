import os, requests
from langchain.tools import tool

API_URL   = "https://apiperu.dev/api/ruc_sunat"
#token para colocarlo en redis
API_TOKEN = os.getenv("APIPERU_TOKEN")

@tool
def consultar_datos_ruc(ruc: str) -> dict:
    """Devuelve la ficha SUNAT de un número de RUC peruano."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        res = requests.post(API_URL, headers=headers, json={"ruc": ruc}, timeout=10)
        res.raise_for_status()
        data = res.json()

        if not data.get("success"):
            return {"error": data.get("message", "RUC inválido")}

        return data["data"]

    except requests.exceptions.RequestException as e:
        return {"error": f"Error HTTP: {str(e)}"}
    except Exception as e:
        return {"error": f"Error general: {str(e)}"}