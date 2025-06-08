from langsmith import traceable
from ...models.state import RISAState
from ...config.llm_config import get_default_llm

# Initialize LLM using the abstraction
llm = get_default_llm()

@traceable
def investment_strategy(state: RISAState) -> RISAState:
    """Generate investment strategies based on market conditions and user profile"""
    print("🔄 Investment Strategy Analysis...")
    
    # Use LLM to generate investment strategy
    prompt = f"""
    Based on the following data, recommend investment strategies:
    
    Market Phase: {state['cycle_phase']}
    Property Valuation: {state['property_valuation']}
    Policy Impact: {state['policy_impact']}
    User Query: {state['user_query']}
    
    Provide specific investment strategies considering:
    1. Current market phase
    2. Risk tolerance
    3. Investment timeline
    4. Market conditions
    
    Format the response with clear strategies and reasoning.
    """
    
    try:
        response = llm.invoke(prompt)
        
        # Default strategy based on market cycle
        default_strategies = {
            "expansion": {
                "primary": "growth_focused",
                "secondary": "cash_flow",
                "risk_level": "moderate",
                "timeline": "medium_term"
            },
            "peak": {
                "primary": "cash_flow",
                "secondary": "defensive",
                "risk_level": "conservative",
                "timeline": "short_term"
            },
            "contraction": {
                "primary": "value_buying",
                "secondary": "long_term_hold",
                "risk_level": "aggressive",
                "timeline": "long_term"
            },
            "trough": {
                "primary": "accumulation",
                "secondary": "renovation",
                "risk_level": "aggressive",
                "timeline": "long_term"
            }
        }
        
        current_strategy = default_strategies.get(state['cycle_phase'], default_strategies['expansion'])
        
        state["investment_strategy"] = {
            "recommended_strategy": current_strategy,
            "llm_analysis": response.content,
            "market_alignment": state['cycle_phase'],
            "confidence_score": 0.8,
            "key_considerations": [
                "Market cycle timing",
                "Risk management",
                "Diversification",
                "Exit strategy"
            ]
        }
        
    except Exception as e:
        print(f"LLM call failed: {e}")
        raise e
    
    print(f"✅ Investment strategy generated for {state['cycle_phase']} market")
    return state 