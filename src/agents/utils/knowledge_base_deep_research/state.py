from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    Represents the state of the knowledge base agent.
    """
    query: str
    messages: List[Dict[str, Any]]
    documents: str
    answer: str
    iteration: int
    rewritten_query: str
    grade: str
    max_iterations: int 