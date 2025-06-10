#!/usr/bin/env python3
"""
Test script for Web Search functionality
"""

import os
import sys
from typing import Any
from langchain_core.messages import AIMessage

# Add parent directory to Python path to find src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.core.web_search import (
    get_web_search_agent,
    check_if_web_search_needed,
    search_current_information,
    analyze_search_results,
    create_web_search_agent
)

def check_api_keys():
    """Check for necessary API keys."""
    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not tavily_key:
        print("❌ TAVILY_API_KEY not found. Web search tests will fail.")
        return False
    if not openai_key:
        print("❌ OPENAI_API_KEY not found. LLM-based tests will fail.")
        return False
        
    print(f"✅ TAVILY_API_KEY found: {tavily_key[:8]}...")
    print(f"✅ OPENAI_API_KEY found: {openai_key[:8]}...")
    return True

def test_tool_check_if_web_search_needed():
    """Test the check_if_web_search_needed tool."""
    print("\n🤔 Testing Tool: check_if_web_search_needed")
    print("-" * 50)
    
    test_queries = [
        ("current housing prices in Tehran", True),
        ("latest real estate market news", True),
        ("what is inflation", False),
        ("real estate investment principles", False),
        ("today's mortgage rates in Iran", True)
    ]
    
    for query, expected in test_queries:
        try:
            result = check_if_web_search_needed.invoke(query)
            status = "✅" if result == expected else "⚠️"
            print(f"  {status} '{query}' -> {result} (expected: {expected})")
        except Exception as e:
            print(f"  ❌ Error testing '{query}': {e}")

def test_tool_search_current_information():
    """Test the search_current_information tool."""
    print("\n🔍 Testing Tool: search_current_information")
    print("-" * 50)
    
    query = "housing prices Tehran current"
    try:
        print(f"  Query: '{query}'")
        results = search_current_information.invoke({"query": query, "max_results": 3})
        
        if results and len(results) > 0:
            print(f"     ✅ Found {len(results)} results")
            for j, result in enumerate(results[:2], 1):
                title = result.get('title', 'No title')[:50]
                url = result.get('url', 'No URL')
                score = result.get('score', 0)
                print(f"       {j}. {title}... (Score: {score:.2f})")
                print(f"          URL: {url}")
        else:
            print(f"     ⚠️  No results returned")
            
    except Exception as e:
        print(f"     ❌ Error: {e}")

def test_tool_analyze_search_results():
    """Test the analyze_search_results tool."""
    print("\n🔀 Testing Tool: analyze_search_results")
    print("-" * 50)
    
    query = "What are current housing market trends in Iran?"
    mock_search_results = [
        {
            "title": "Iran Real Estate Market Outlook 2024",
            "content": "The Tehran housing market has seen a 15% increase in prices in the last quarter...",
            "url": "http://example.com/iran-real-estate-2024",
            "score": 0.9
        },
        {
            "title": "Iranian Construction Sector Report",
            "content": "New construction projects are on the rise in major cities, despite economic challenges.",
            "url": "http://example.com/iran-construction-report",
            "score": 0.85
        }
    ]
    
    try:
        print(f"  Query: '{query}'")
        answer = analyze_search_results.invoke({"query": query, "search_results": mock_search_results})
        
        if answer and isinstance(answer, str) and len(answer) > 20:
            print("     ✅ Answer generated successfully")
            answer_preview = answer.replace('\n', ' ').strip()[:150]
            print(f"     💬 Answer Preview: {answer_preview}...")
        else:
            print("     ⚠️  Answer generation failed or produced a minimal response.")
            
    except Exception as e:
        print(f"     ❌ Error: {e}")

def test_full_agent_flow():
    """Test the full web search agent flow."""
    print("\n🚀 Testing Full Web Search Agent Flow")
    print("=" * 50)
    
    try:
        print("  🔄 Initializing Web Search Agent...")
        agent = create_web_search_agent(with_memory=False)
        print("  ✅ Agent initialized successfully")
    except Exception as e:
        print(f"  ❌ Error initializing agent: {e}")
        return

    query = "What are the latest mortgage rates in Iran?"
    
    try:
        print(f"\n  ▶️  Invoking agent with query: '{query}'")
        
        input_data = {"messages": [("user", query)]}
        
        final_chunk = None
        for chunk in agent.stream(input_data):
            final_chunk = chunk
        
        print("\n  🏁 Agent finished processing")
        
        final_state = None
        # The final answer from the ReAct agent is in the 'agent' key of the last chunk
        if final_chunk and "agent" in final_chunk:
            agent_output = final_chunk.get("agent", {})
            messages = agent_output.get("messages", [])
            if messages and isinstance(messages[-1], AIMessage):
                final_state = messages[-1].content
        
        if final_state:
            print("  ✅ Final answer received from agent.")
            print(f"  💬 Agent's Answer:\n{final_state}")
        else:
            print("  ⚠️  Agent did not produce a final answer.")
            print(f"    Last chunk from stream: {final_chunk}")

    except Exception as e:
        print(f"  ❌ Error during agent invocation: {e}")

def test_get_web_search_agent_creation():
    """Test that get_web_search_agent returns a valid agent."""
    print("\n🔧 Testing Factory: get_web_search_agent")
    print("-" * 50)
    try:
        agent = get_web_search_agent()
        if hasattr(agent, 'invoke') and hasattr(agent, 'stream'):
             print("✅ get_web_search_agent returned a valid agent object.")
        else:
             print("❌ get_web_search_agent did not return a valid agent.")
    except Exception as e:
        print(f"❌ Error creating agent with get_web_search_agent: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("     Running Web Search Agent Tests")
    print("=" * 60)
    
    if not check_api_keys():
        print("\nHalting tests due to missing API keys.")
    else:
        test_tool_check_if_web_search_needed()
        test_tool_search_current_information()
        test_tool_analyze_search_results()
        test_full_agent_flow()
        test_get_web_search_agent_creation()

    print("\n" + "=" * 60)
    print("Web Search test suite completed!")
    print("=" * 60)

