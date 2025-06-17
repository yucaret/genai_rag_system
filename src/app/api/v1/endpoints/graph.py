from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src.app.infrastructure.llm.rag_graph_exporter import export_langgraph_to_mermaid

router = APIRouter()

@router.get("/graph/diagram", response_class=PlainTextResponse)
def get_langgraph_diagram():
    mermaid_code = export_langgraph_to_mermaid()
    return mermaid_code
