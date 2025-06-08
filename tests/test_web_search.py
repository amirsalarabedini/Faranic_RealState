#!/usr/bin/env python3
"""
Test script for Web Search functionality
"""

import os
import sys
# Add parent directory to Python path to find src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.core.web_search import WebSearchAgent, get_web_search_agent

def test_web_search():
    """Test the web search system"""
    print("🌐 Testing Web Search Agent")
    print("=" * 50)
    
    # Check API keys
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print("❌ TAVILY_API_KEY not found. Web search tests will fail.")
        return False
    else:
        print(f"✅ TAVILY_API_KEY found: {tavily_key[:8]}...")
    
    # Test WebSearchAgent initialization
    try:
        print("\n🔄 Initializing Web Search Agent...")
        agent = WebSearchAgent()
        print("✅ Web Search Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Web Search Agent: {e}")
        return False
    
    # Test web search decision logic
    print("\n🤔 Testing Web Search Decision Logic:")
    test_queries = [
        ("current housing prices in Tehran", True),
        ("latest real estate market news", True),
        ("what is inflation", False),
        ("real estate investment principles", False),
        ("today's mortgage rates in Iran", True)
    ]
    
    for query, expected in test_queries:
        try:
            result = agent.should_use_web_search(query)
            status = "✅" if result == expected else "⚠️"
            print(f"  {status} '{query}' -> {result} (expected: {expected})")
        except Exception as e:
            print(f"  ❌ Error testing '{query}': {e}")
    
    # Test basic web search
    print("\n🔍 Testing Web Search:")
    search_queries = [
        "real estate market trends Iran 2024",
        "housing prices Tehran current",
        "mortgage rates Iran latest"
    ]
    
    for i, query in enumerate(search_queries, 1):
        try:
            print(f"\n  {i}. Query: '{query}'")
            results = agent.search_web(query, max_results=3)
            
            if results and len(results) > 0:
                print(f"     ✅ Found {len(results)} results")
                for j, result in enumerate(results[:2], 1):  # Show first 2 results
                    title = result.get('title', 'No title')[:50]
                    url = result.get('url', 'No URL')
                    score = result.get('score', 0)
                    print(f"       {j}. {title}... (Score: {score:.2f})")
                    print(f"          URL: {url}")
            else:
                print(f"     ⚠️  No results returned")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Test result synthesis
    print("\n🔀 Testing Result Synthesis:")
    synthesis_test_queries = [
        "What are current housing market trends in Iran?",
        "What are the latest mortgage rates?",
        "Recent real estate news in Tehran"
    ]
    
    for i, query in enumerate(synthesis_test_queries, 1):
        try:
            print(f"\n  {i}. Query: '{query}'")
            print("     🔄 Processing...")
            
            result = agent.process_web_query(query)
            
            if result and 'answer' in result:
                print(f"     ✅ Answer generated")
                print(f"     📊 Source: {result.get('source', 'unknown')}")
                print(f"     📅 Timestamp: {result.get('timestamp', 'N/A')}")
                print(f"     📄 Results count: {len(result.get('results', []))}")
                
                # Show answer preview
                answer_preview = result['answer'][:200].replace('\n', ' ').strip()
                print(f"     💬 Answer: {answer_preview}...")
                
            else:
                print(f"     ⚠️  No answer generated")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    print("\n🎉 Web Search test completed!")
    return True

def test_global_web_search_agent():
    """Test the global web search agent instance"""
    print("\n🌍 Testing Global Web Search Agent:")
    print("-" * 40)
    
    try:
        # Test getting global instance
        agent1 = get_web_search_agent()
        agent2 = get_web_search_agent()
        
        # Should be the same instance
        if agent1 is agent2:
            print("✅ Global instance working correctly (singleton pattern)")
        else:
            print("⚠️  Global instance not following singleton pattern")
        
        # Test functionality through global instance
        result = agent1.should_use_web_search("current market prices")
        print(f"✅ Global agent functionality test: {result}")
        
    except Exception as e:
        print(f"❌ Error testing global agent: {e}")

def test_api_connectivity():
    """Test API connectivity and configuration"""
    print("\n🔌 Testing API Connectivity:")
    print("-" * 30)
    
    # Check environment variables
    required_vars = ["TAVILY_API_KEY", "OPENAI_API_KEY"]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:8]}...")
        else:
            print(f"❌ {var}: Not found")
    
    # Test basic connectivity
    try:
        agent = get_web_search_agent()
        
        # Simple test query
        test_result = agent.search_web("test query", max_results=1)
        if test_result:
            print("✅ Web search API connectivity confirmed")
        else:
            print("⚠️  Web search API returned empty results")
            
    except Exception as e:
        print(f"❌ API connectivity error: {e}")

if __name__ == "__main__":
    # Check critical environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found. Some tests may fail.")
    
    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  Warning: TAVILY_API_KEY not found. Web search tests will fail.")
    
    # Run all tests
    test_api_connectivity()
    success = test_web_search()
    test_global_web_search_agent()
    
    print("\n" + "=" * 50)
    print("Web Search test completed! Check the results above.")

