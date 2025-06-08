from typing import TypedDict, Dict, Any

class RISAState(TypedDict):
    raw_data: Dict[str, Any]
    book_facts: Dict[str, Any]
    cycle_phase: str
    cycle_analysis: Dict[str, Any]  # Enhanced cycle analysis with confidence, reasoning, etc.
    property_valuation: Dict[str, Any]
    policy_impact: Dict[str, Any]
    user_query: str
    answer: str
    investment_strategy: Dict[str, Any]
    rental_analysis: Dict[str, Any]
    macro_analysis: Dict[str, Any]
    query_intent: Dict[str, Any]