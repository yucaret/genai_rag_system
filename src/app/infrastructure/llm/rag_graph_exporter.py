from langgraph.graph import StateGraph, END
from typing import Dict, Any
from src.app.infrastructure.llm.rag_chain_instance import build_rag_langgraph

def export_langgraph_to_mermaid() -> str:
    graph = build_rag_langgraph()
    graph_structure = graph.get_graph()
    
    mermaid = ["graph TD"]

    # Add nodes
    for node in graph_structure.nodes:
        mermaid.append(f'    {node}(["{node}"])')

    # Add edges
    for edge in graph_structure.edges:
        mermaid.append(f'    {edge.source} --> {edge.target}')

    # Styling
    mermaid.append("    style query_llm fill:#f9f,stroke:#333,stroke-width:2px")
    mermaid.append("    style decide_path fill:#ffd,stroke:#111,stroke-width:2px")

    return "\n".join(mermaid)
