from langsmith import traceable
from ...models.state import RISAState
from ...config.llm_config import get_default_llm

# Initialize LLM using the abstraction
llm = get_default_llm()

@traceable
def macro_analysis(state: RISAState) -> RISAState:
    """Analyze macroeconomic factors affecting real estate market based on the data provided by orchestrator"""
    print("🔄 Macroeconomic Analysis...")
    
    # Use LLM to analyze macroeconomic factors