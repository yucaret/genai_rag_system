from langgraph.graph import StateGraph, END
from typing import Dict, Any, Literal, Optional
from pydantic import BaseModel
#from src.app.infrastructure.llm.chains import RAGChain
from src.app.infrastructure.llm.rag_container import rag_chain
import logging
logger = logging.getLogger("genai")

# Define the state model properly
class RAGState(BaseModel):
    question: str
    search_section: Optional[str] = None
    answer: Optional[str] = None
    used_doc: Optional[str] = None
    next_node: Optional[str] = None 

# Initialize the graph
graph = StateGraph(RAGState)

# === Decision Node ===
def decide_path(state: RAGState) -> Dict[str, Any]:
    question = state.question.lower()
    if "resumen" in question or "executivo" in question:
        return {"search_section": "summary", "next_node": "route_summary"}
    elif "anexo" in question or "anexos" in question:
        return {"search_section": "annex", "next_node": "route_annex"}
    else:
        return {"search_section": "all", "next_node": "route_all"}

# === Routing Nodes ===
def route_summary(state: RAGState) -> Dict[str, Any]:
    return {"next_node": "query_llm"}

def route_annex(state: RAGState) -> Dict[str, Any]:
    return {"next_node": "query_llm"}

def route_all(state: RAGState) -> Dict[str, Any]:
    return {"next_node": "query_llm"}

# === Final query node ===
def query_llm(state: RAGState) -> Dict[str, Any]:
    response = rag_chain.run(
        query=state.question,
        section=state.search_section
    )
    return {
        "answer": response["answer"],
        "used_doc": response["doc_id"],
        "next_node": END
    }

# === LangGraph Definition ===
def build_rag_langgraph():
    graph = StateGraph(RAGState)
    
    # Add nodes
    graph.add_node("decide_path", decide_path)
    graph.add_node("route_summary", route_summary)
    graph.add_node("route_annex", route_annex)
    graph.add_node("route_all", route_all)
    graph.add_node("query_llm", query_llm)

    # Set up conditional routing
    graph.add_conditional_edges(
        "decide_path",
        lambda state: state.next_node,  # Now this will work
        {
            "route_summary": "route_summary",
            "route_annex": "route_annex",
            "route_all": "route_all"
        }
    )

    # Add regular edges
    graph.add_edge("route_summary", "query_llm")
    graph.add_edge("route_annex", "query_llm")
    graph.add_edge("route_all", "query_llm")

    graph.set_entry_point("decide_path")
    graph.set_finish_point("query_llm")

    return graph.compile()

# === Run LangGraph ===
def run_rag_with_langgraph(question: str, use_cache=False) -> Dict[str, str]:
    rag_flow = build_rag_langgraph()
    initial_state = {
        "question": question,
        "search_section": None,
        "answer": None,
        "used_doc": None
    }
    try:
        result = rag_flow.invoke(initial_state)
        return {
            "answer": result.get("answer", "No answer generated"),
            "doc_id": result.get("used_doc", "unknown")
        }
    except Exception as e:
        logger.error(f"Error in RAG flow: {str(e)}")
        return {
            "answer": "Error processing your question",
            "doc_id": "error"
        }