from langsmith import traceable
from langgraph.graph import StateGraph, END
from ...models.state import RISAState
from ...config.llm_config import get_default_llm
from typing import List

# Import all agents
from ..core import (
    data_ingest,
    market_cycle,
    query_understanding,
    generate_report
)
from ..analysis import (
    valuation_analysis,
    policy_simulation,
    investment_strategy,
    rental_market,
    macro_analysis
)

# Initialize LLM using the abstraction
llm = get_default_llm()

def create_risa_graph() -> StateGraph:
    """Create and compile the RISA workflow graph using StateGraph"""
    
    # Create the StateGraph
    workflow = StateGraph(RISAState)
    
    # Add all agent nodes with "_node" suffix to avoid state key conflicts
    workflow.add_node("query_understanding_node", query_understanding)
    workflow.add_node("data_ingest_node", data_ingest)
    workflow.add_node("market_cycle_node", market_cycle)
    workflow.add_node("valuation_analysis_node", valuation_analysis)
    workflow.add_node("policy_simulation_node", policy_simulation)
    workflow.add_node("investment_strategy_node", investment_strategy)
    workflow.add_node("rental_market_node", rental_market)
    workflow.add_node("macro_analysis_node", macro_analysis)
    workflow.add_node("generate_report_node", generate_report)
    
    # Set entry point - always start with data ingestion and query understanding
    workflow.set_entry_point("query_understanding_node")

    # Add conditional routing after query understanding using LLM-based decision making
    workflow.add_conditional_edges(
        "query_understanding_node",
        route_after_query_understanding,
        {
            "data_ingest": "data_ingest_node",
            "market_cycle": "market_cycle_node",
            "valuation_analysis": "valuation_analysis_node",
            "policy_simulation": "policy_simulation_node",
            "rental_market": "rental_market_node",
            "macro_analysis": "macro_analysis_node",
            "investment_strategy": "investment_strategy_node",
            "generate_report": "generate_report_node"
        }
    )
    
    # Add conditional routing after market_cycle based on user intent
    workflow.add_conditional_edges(
        "market_cycle_node",
        route_based_on_intent,
        {
            "valuation_analysis": "valuation_analysis_node",
            "policy_simulation": "policy_simulation_node",
            "rental_market": "rental_market_node",
            "macro_analysis": "macro_analysis_node",
            "investment_strategy": "investment_strategy_node"
        }
    )
    
    # Route from specialized analysis back to appropriate next steps
    workflow.add_conditional_edges(
        "valuation_analysis_node",
        route_after_valuation,
        {
            "investment_strategy": "investment_strategy_node",
            "rental_market": "rental_market_node",
            "macro_analysis": "macro_analysis_node",
            "generate_report": "generate_report_node"
        }
    )
    
    workflow.add_conditional_edges(
        "policy_simulation_node",
        route_after_policy,
        {
            "macro_analysis": "macro_analysis_node",
            "investment_strategy": "investment_strategy_node",
            "generate_report": "generate_report_node"
        }
    )
    
    workflow.add_conditional_edges(
        "rental_market_node",
        route_after_rental,
        {
            "investment_strategy": "investment_strategy_node",
            "macro_analysis": "macro_analysis_node",
            "generate_report": "generate_report_node"
        }
    )
    
    workflow.add_conditional_edges(
        "investment_strategy_node",
        route_after_investment,
        {
            "macro_analysis": "macro_analysis_node",
            "generate_report": "generate_report_node"
        }
    )
    
    workflow.add_conditional_edges(
        "macro_analysis_node",
        route_after_macro,
        {
            "generate_report": "generate_report_node"
        }
    )
    
    # Final report always ends the workflow
    workflow.add_edge("generate_report_node", END)
    
    return workflow.compile()

def route_based_on_intent(state: RISAState) -> str:
    """Route to the first specialized agent based on user intent"""
    query_intent = state.get('query_intent', {})
    user_type = query_intent.get('user_type', 'investor')
    primary_intent = query_intent.get('primary_intent', 'analyze')
    relevant_modules = query_intent.get('relevant_modules', [])
    
    # Prioritize routing based on user type and intent
    if user_type == 'government' or 'policy' in relevant_modules:
        return "policy_simulation"
    elif user_type == 'renter' or primary_intent == 'rent' or 'rental' in relevant_modules:
        return "rental_market"
    elif user_type in ['investor', 'homebuyer'] or 'valuation' in relevant_modules:
        return "valuation_analysis"
    else:
        return "macro_analysis"

def route_after_valuation(state: RISAState) -> str:
    """Route after valuation analysis"""
    query_intent = state.get('query_intent', {})
    user_type = query_intent.get('user_type', 'investor')
    relevant_modules = query_intent.get('relevant_modules', [])
    
    # Check if we need rental analysis
    if user_type == 'investor' and ('rental' in relevant_modules or 'rent' in state.get('user_query', '').lower()):
        return "rental_market"
    # Check if we need investment strategy
    elif user_type == 'investor':
        return "investment_strategy"
    else:
        return "macro_analysis"

def route_after_policy(state: RISAState) -> str:
    """Route after policy simulation"""
    query_intent = state.get('query_intent', {})
    user_type = query_intent.get('user_type', 'investor')
    
    if user_type == 'investor':
        return "investment_strategy"
    else:
        return "macro_analysis"

def route_after_rental(state: RISAState) -> str:
    """Route after rental market analysis"""
    query_intent = state.get('query_intent', {})
    user_type = query_intent.get('user_type', 'investor')
    
    if user_type == 'investor' and not state.get('investment_strategy'):
        return "investment_strategy"
    elif not state.get('macro_analysis'):
        return "macro_analysis"
    else:
        return "generate_report"

def route_after_investment(state: RISAState) -> str:
    """Route after investment strategy"""
    # Always go to macro analysis if not done, otherwise report
    if not state.get('macro_analysis'):
        return "macro_analysis"
    else:
        return "generate_report"

def route_after_macro(state: RISAState) -> str:
    """Route after macro analysis - always go to report"""
    return "generate_report"

def route_after_query_understanding(state: RISAState) -> str:
    """
    Intelligent routing after query understanding using LLM-based decision making.
    This function makes an LLM call to determine the most appropriate next step 
    based on the query understanding results and user context.
    """
    query_intent = state.get('query_intent', {})
    user_query = state.get('user_query', '')
    
    # Create a comprehensive routing prompt for the LLM
    routing_prompt = f"""
    You are a routing agent for a real estate investment analysis system (RISA).
    Based on the user query and intent analysis, determine the most appropriate next step.
    
    User Query: {user_query}
    
    Query Analysis:
    - User Type: {query_intent.get('user_type', 'unknown')}
    - Primary Intent: {query_intent.get('primary_intent', 'unknown')}
    - Information Needs: {query_intent.get('information_needs', [])}
    - Relevant Modules: {query_intent.get('relevant_modules', [])}
    - Expertise Level: {query_intent.get('expertise_level', 'beginner')}
    - Key Topics: {query_intent.get('key_topics', [])}
    
    Available routing options:
    1. "data_ingest" - For queries needing fresh market data collection
    2. "market_cycle" - For market timing and cycle analysis
    3. "valuation_analysis" - For property valuation and pricing analysis
    4. "policy_simulation" - For government policy impact analysis
    5. "rental_market" - For rental market and yield analysis
    6. "macro_analysis" - For macroeconomic impact analysis
    7. "investment_strategy" - For investment strategy recommendations
    8. "generate_report" - For simple information requests or summaries
    
    Routing Logic:
    - If user needs current market data or mentions specific locations/properties: route to "data_ingest"
    - If user asks about market timing, cycles, or "when to buy/sell": route to "market_cycle"  
    - If user asks about property values, pricing, or "how much is worth": route to "valuation_analysis"
    - If user is government type or asks about policy impacts: route to "policy_simulation"
    - If user asks about rental yields, rent prices, or is a renter: route to "rental_market"
    - If user asks about economic factors, inflation, interest rates: route to "macro_analysis"
    - If user asks for investment advice, portfolio strategy: route to "investment_strategy"
    - If user asks simple questions or wants a general report: route to "generate_report"
    
    Consider the user's expertise level and provide the most valuable starting point.
    
    Respond with ONLY the routing option (e.g., "valuation_analysis").
    """
    
    # Make LLM call to determine routing
    response = llm.invoke(routing_prompt)
    routing_decision = response.content.strip().replace('"', '').lower()
    
    print(f"🎯 LLM Routing Decision: {routing_decision}")
    return routing_decision

@traceable
def orchestrator(state: RISAState) -> RISAState:
    """Main orchestrator using LangGraph StateGraph"""
    print("🎯 RISA LangGraph Orchestrator Starting...")
    print(f"📝 User Query: {state['user_query']}")
    
    try:
        # Create and run the graph
        app = create_risa_graph()
        print("📊 Graph created successfully")
        
        # Save the graph visualization to file (optional)
        try:
            graph_png_bytes = app.get_graph().draw_mermaid_png()
            with open("risa_graph.png", "wb") as f:
                f.write(graph_png_bytes)
            print("📈 Graph visualization saved to risa_graph.png")
        except Exception as viz_error:
            print(f"⚠️ Could not save graph visualization: {viz_error}")
        
        print("\n🔄 Executing RISA Analysis Workflow...")
        result_state = app.invoke(state)
        
        print("\n✅ RISA Analysis Complete!")
        return result_state
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        raise e

# Legacy functions for compatibility
def determine_execution_plan(state: RISAState) -> List[str]:
    """Legacy function - determine which agents to run based on query intent and user type"""
    # This is kept for backward compatibility but not used in the graph-based approach
    query_intent = state.get('query_intent', {})
    user_type = query_intent.get('user_type', 'investor')
    primary_intent = query_intent.get('primary_intent', 'analyze')
    relevant_modules = query_intent.get('relevant_modules', [])
    
    # Base agents that almost always run
    execution_plan = ['market_cycle_node']
    
    # Add agents based on user type and intent
    if user_type == 'investor':
        execution_plan.extend(['valuation_analysis_node', 'investment_strategy_node', 'macro_analysis_node'])
        if primary_intent == 'rent' or 'rental' in relevant_modules:
            execution_plan.append('rental_market_node')
    
    elif user_type == 'homebuyer':
        execution_plan.extend(['valuation_analysis_node', 'macro_analysis_node'])
    
    elif user_type == 'renter':
        execution_plan.extend(['rental_market_node', 'macro_analysis_node'])
    
    elif user_type == 'developer':
        execution_plan.extend(['valuation_analysis_node', 'policy_simulation_node', 'macro_analysis_node'])
    
    elif user_type == 'government':
        execution_plan.extend(['policy_simulation_node', 'macro_analysis_node'])
    
    # Add specific modules mentioned in query intent
    for module in relevant_modules:
        if module not in execution_plan and module in [
            'valuation_analysis_node', 'policy_simulation_node', 'investment_strategy_node',
            'rental_market_node', 'macro_analysis_node'
        ]:
            execution_plan.append(module)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_plan = []
    for agent in execution_plan:
        if agent not in seen:
            seen.add(agent)
            unique_plan.append(agent)
    
    return unique_plan

if __name__ == "__main__":
    state = RISAState(user_query="What is the current market cycle?")
    orchestrator(state)
