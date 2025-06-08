from langsmith import traceable
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from typing import Dict, Any, List, Optional, Annotated
import os
import sys
import json
from datetime import datetime

# Handle imports for both direct execution and module imports
try:
    from src.config.llm_config import get_llm
except ImportError:
    # If running directly, try to add the project root to the path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    sys.path.insert(0, project_root)
    try:
        from src.config.llm_config import get_llm
    except ImportError:
        # Fallback: create a simple LLM getter
        def get_llm():
            return init_chat_model("anthropic:claude-3-haiku-latest", temperature=0.1)
        print("⚠️  Using fallback LLM configuration")

# Initialize global search instance
_tavily_search = None
_preferred_domains = [
    "https://cbi.ir/",
    "https://www.cbi.ir/fa/Pages/default.aspx", 
    "https://amar.org.ir/",
    "https://www.amar.org.ir/fa/Pages/default.aspx",
]

def get_tavily_search():
    """Get or create global TavilySearch instance"""
    global _tavily_search
    if _tavily_search is None:
        _tavily_search = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))
    return _tavily_search

@tool
def check_if_web_search_needed(query: str) -> bool:
    """
    Determine if a query requires current, real-time information from the web.
    
    Args:
        query: The user's question or search query
        
    Returns:
        bool: True if web search is needed for current/real-time data, False otherwise
    """
    try:
        model = get_llm()
        prompt = (
            "Determine if the following query requires current, real-time information from the web "
            "or if it can be answered with historical/theoretical knowledge about real estate. "
            "Answer 'yes' if it needs current market data, recent news, current prices, or real-time information. "
            "Answer 'no' if it's about general real estate concepts, historical trends, or theoretical knowledge.\n"
            f"Query: {query}\n"
            "Needs web search (yes/no):"
        )
        
        response = model.invoke([{"role": "user", "content": prompt}])
        return "yes" in response.content.lower()
    except Exception as e:
        print(f"❌ Error determining web search need: {e}")
        return False

@tool
def search_current_information(
    query: str,
    max_results: Annotated[int, "Maximum number of results to return"] = 5,
    boost_iranian_sources: Annotated[bool, "Whether to boost Iranian real estate sources"] = True
) -> List[Dict[str, Any]]:
    """
    Search the web for current information with preference for Iranian real estate sources.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return (default: 5)
        boost_iranian_sources: Whether to boost scores for Iranian sources (default: True)
        
    Returns:
        List of search results with title, content, url, and score
    """
    try:
        search = get_tavily_search()
        print(f"🌐 Searching web for: {query}")
        
        # Enhance query for Iranian real estate context if needed
        enhanced_query = query if "Iran" in query or "Tehran" in query else f"{query} Iran real estate"
        
        # Search parameters
        search_params = {
            "query": enhanced_query,
            "max_results": max_results * 2,  # Get more results for better boosting
            "search_depth": "advanced"
        }
        
        print("🌍 Searching across all domains with preference boosting")
        results = search.invoke(search_params)
        
        # Handle response structure
        if isinstance(results, dict) and 'results' in results:
            search_results = results['results']
        elif isinstance(results, list):
            search_results = results
        else:
            search_results = []
        
        # Process and boost Iranian sources if requested
        processed_results = []
        for result in search_results:
            processed_result = {
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0)
            }
            
            # Boost Iranian sources
            if boost_iranian_sources:
                url = processed_result["url"]
                is_iranian = any(domain in url for domain in _preferred_domains)
                if is_iranian:
                    original_score = processed_result["score"]
                    boosted_score = min(original_score * 1.5, 1.0)
                    processed_result["score"] = boosted_score
                    processed_result["domain_boosted"] = True
                    print(f"🎯 Boosted Iranian source: {url}")
                else:
                    processed_result["domain_boosted"] = False
            
            processed_results.append(processed_result)
        
        # Sort by score and limit results
        processed_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        final_results = processed_results[:max_results]
        
        print(f"✅ Found {len(final_results)} web results")
        if boost_iranian_sources:
            boosted_count = sum(1 for r in final_results if r.get("domain_boosted", False))
            if boosted_count > 0:
                print(f"🚀 {boosted_count} results boosted from Iranian sources")
        
        return final_results
        
    except Exception as e:
        print(f"❌ Error searching web: {e}")
        return []

@tool
def analyze_search_results(
    query: str, 
    search_results: List[Dict[str, Any]]
) -> str:
    """
    Analyze and synthesize web search results into a comprehensive answer.
    
    Args:
        query: The original user query
        search_results: List of search results from search_current_information
        
    Returns:
        Synthesized answer based on the search results
    """
    if not search_results:
        return "No current web information found for this query."
    
    try:
        # Prepare context from top results
        context_parts = []
        for i, result in enumerate(search_results[:3], 1):
            context_parts.append(
                f"Source {i}: {result['title']}\n"
                f"{result['content']}\n"
                f"URL: {result['url']}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        model = get_llm()
        synthesis_prompt = (
            "You are a real estate analyst specializing in Iranian markets. "
            "Based on the following current web search results, provide a comprehensive answer to the user's question. "
            "Focus on current market conditions, recent trends, and up-to-date information. "
            "Cite sources when possible and highlight Iranian market specifics.\n\n"
            f"Question: {query}\n\n"
            f"Current Web Information:\n{context}\n\n"
            "Provide a detailed, well-structured answer:"
        )
        
        response = model.invoke([{"role": "user", "content": synthesis_prompt}])
        return response.content.strip()
        
    except Exception as e:
        print(f"❌ Error synthesizing web results: {e}")
        return f"Error processing web search results: {e}"

def create_web_search_agent(
    with_memory: bool = True,
    system_prompt: str = None
):
    """
    Create a web search agent using LangGraph's create_react_agent.
    
    Args:
        with_memory: Whether to enable conversation memory (default: True)
        system_prompt: Custom system prompt (optional)
        
    Returns:
        Configured LangGraph agent
    """
  
    model = get_llm()
    
    # Define tools for the agent
    tools = [
        check_if_web_search_needed,
        search_current_information,
        analyze_search_results
    ]
    
    # Default system prompt
    if system_prompt is None:
        system_prompt = (
            "You are a specialized Iranian real estate web search agent. "
            "Your role is to find and analyze current, up-to-date information about real estate markets, "
            "particularly focusing on Iranian markets when relevant.\n\n"
            "When a user asks a question:\n"
            "1. First determine if the question requires current/real-time information using check_if_web_search_needed\n"
            "2. If web search is needed, use search_current_information to find relevant data\n"
            "3. Then use analyze_search_results to synthesize the findings into a comprehensive answer\n"
            "4. If web search is not needed, answer using your existing knowledge\n\n"
            "Always prioritize current, factual information and cite sources when available. "
            "Focus on Iranian real estate sources when relevant to provide the most accurate local market insights."
        )
    
    # Create the agent
    agent_config = {
        "model": model,
        "tools": tools,
        "prompt": system_prompt
    }
    
    # Add memory if requested
    if with_memory:
        checkpointer = InMemorySaver()
        agent_config["checkpointer"] = checkpointer
        print("✅ Web search agent created with memory enabled")
    else:
        print("✅ Web search agent created without memory")
    
    agent = create_react_agent(**agent_config)
    
    print(f"🚀 Iranian Real Estate Web Search Agent initialized")
    print(f"🔧 Tools: {len(tools)} available")
    print(f"🎯 Preferred domains: {len(_preferred_domains)} Iranian sources")
    
    return agent

def get_web_search_agent(**kwargs):
    """
    Get a pre-configured web search agent instance.
    
    Args:
        **kwargs: Configuration options for create_web_search_agent
        
    Returns:
        Configured LangGraph agent
    """
    return create_web_search_agent(**kwargs)

# Example usage and testing
if __name__ == "__main__":
    # Create agent with default configuration
    agent = create_web_search_agent(with_memory=True)
    
    # Example query with memory
    config = {"configurable": {"thread_id": "demo-session"}}
    
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "What are the current real estate prices in Tehran?"}]},
        config=config
    )
    
    print("🎉 Agent Response:")
    # Handle the response properly - it's a state dict with messages
    if isinstance(response, dict) and "messages" in response:
        print(response["messages"][-1].content)