from pydantic import BaseModel
from typing import Optional, Literal

# State that flows in the LangGraph
class RAGState(BaseModel):
    question: str
    search_section: Optional[Literal["summary", "annex", "all"]] = None
    context: Optional[str] = None
    answer: Optional[str] = None

# The decision return type (valid options for branching)
Decision = Literal["summary", "annex", "all"]
