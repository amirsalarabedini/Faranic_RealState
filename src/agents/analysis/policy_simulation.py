from langsmith import traceable
from src.models.state import RISAState

@traceable
def policy_simulation(state: RISAState) -> RISAState:
    """Simulate policy impact on real estate based on the data provided by orchestrator"""
