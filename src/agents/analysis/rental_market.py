from langsmith import traceable
from src.models.state import RISAState
from src.configs.llm_config import get_default_llm

# Initialize LLM using the abstraction
llm = get_default_llm()

@traceable
def rental_market(state: RISAState) -> RISAState:
    """Analyze rental market and calculate rental yields based on the data provided by orchestrator"""
    print("🔄 Rental Market Analysis...")
    
    # Use LLM to analyze the rental market and calculate rental yields