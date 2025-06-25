from langgraph.graph import StateGraph, END
from typing import Dict, Any, Literal, Optional
from pydantic import BaseModel
#from src.app.infrastructure.llm.chains import RAGChain
from src.app.infrastructure.llm.rag_container import rag_chain
import logging

# agregamos 2025-06-19: agente para responder ruc
import re
from src.app.infrastructure.llm.rag_agent import RAGAgent # nuevo agente
from src.app.infrastructure.llm.providers import OpenAIProvider # fallback LLM
##

logger = logging.getLogger("genai")

# agregamos 2025-06-19: agente para responder ruc
RUC_RE = re.compile(r"\b\d{11}\b") # RUC peruano: tiene 11 dígitos
agent = RAGAgent()
llm_fb = OpenAIProvider()
##

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
    print("rag_chain_instance.py --> def decide_path")
    
    question = state.question.lower()
    
    # agregamos 2025-06-19: ¿Contiene RUC?
    if "ruc" in question or RUC_RE.search(question):
        return {"next_node": "route_ruc"}
    ##
    
    if "resumen" in question or "executivo" in question:
        return {"search_section": "summary", "next_node": "route_summary"}
    elif "anexo" in question or "anexos" in question:
        return {"search_section": "annex", "next_node": "route_annex"}
    else:
        return {"search_section": "all", "next_node": "route_all"}

# === Routing Nodes ===
def route_summary(state: RAGState) -> Dict[str, Any]:
    print("rag_chain_instance.py --> def route_summary")
    return {"next_node": "query_llm"}

def route_annex(state: RAGState) -> Dict[str, Any]:
    print("rag_chain_instance.py --> def route_annex")
    return {"next_node": "query_llm"}

def route_all(state: RAGState) -> Dict[str, Any]:
    print("rag_chain_instance.py --> def route_all")
    return {"next_node": "query_llm"}

# agregamos 2025-06-19: Route ruc
def route_ruc(state: RAGState) -> Dict[str, Any]:
    print("rag_chain_instance.py --> def route_ruc")
    return {"next_node": "query_ruc"}
##

# === Final query node ===
def query_llm(state: RAGState) -> Dict[str, Any]:
    print("rag_chain_instance.py --> def query_llm")
    response = rag_chain.run(
        query=state.question,
        section=state.search_section
    )
    return {
        "answer": response["answer"],
        "used_doc": response["doc_id"],
        "next_node": END
    }

# agregamos 2025-06-19: query de ruc
def query_ruc(state: RAGState) -> Dict[str, Any]:
    print("rag_chain_instance.py --> def query_ruc")
    try:
        ## modificado 2025-06-25; que no lea historia
        #answer = agent.run(state.question)
        answer = agent.run(state.question, use_history=False)
        ##
        
        return {"answer": answer, "used_doc": "api_ruc", "next_node": END}
    except Exception as e:
        logger.error(f"Agent RUC error: {e}")
        fb = llm_fb.chat_completion(f"No pude responder: {state.question}")
        return {"answer": fb, "used_doc": "fallback", "next_node": END}
##

# === LangGraph Definition ===
def build_rag_langgraph():
    print("rag_chain_instance.py --> def build_rag_langgraph")
    graph = StateGraph(RAGState)
    
    # Add nodes
    graph.add_node("decide_path", decide_path)
    
    # agregamos 2025-06-19: nodo del query de ruc
    graph.add_node("route_ruc", route_ruc)
    ##
    
    graph.add_node("route_summary", route_summary)
    graph.add_node("route_annex", route_annex)
    graph.add_node("route_all", route_all)
    
    # agregamos 2025-06-19: nodo del query de ruc
    graph.add_node("query_ruc", query_ruc)
    ##
    
    graph.add_node("query_llm", query_llm)

    # Set up conditional routing
    graph.add_conditional_edges(
        "decide_path",
        lambda state: state.next_node,  # Now this will work
        {
            # agregamos 2025-06-19: nodo del query de ruc
            "route_ruc":     "route_ruc",
            ##
            
            "route_summary": "route_summary",
            "route_annex": "route_annex",
            "route_all": "route_all"
        }
    )

    # Add regular edges
    ## agregamos 2025-06-19
    graph.add_edge("route_ruc", "query_ruc")
    ##
    
    graph.add_edge("route_summary", "query_llm")
    graph.add_edge("route_annex", "query_llm")
    graph.add_edge("route_all", "query_llm")

    graph.set_entry_point("decide_path")
    
    # agregamos 2025-06-19
    graph.set_finish_point("query_ruc")
    ##    
    
    graph.set_finish_point("query_llm")

    return graph.compile()

# === Run LangGraph ===
def run_rag_with_langgraph(question: str, use_cache=False) -> Dict[str, str]:
    print("rag_chain_instance.py --> def run_rag_with_langgraph")
    
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