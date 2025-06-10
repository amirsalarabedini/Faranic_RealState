#!/usr/bin/env python3
"""
Test script for Knowledge Base functionality
"""

import os
import sys
# Add parent directory to Python path to find src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.core.knowledge_retriever import KnowledgeRetriever, get_knowledge_retriever

def test_knowledge_base():
    """Test the knowledge base retrieval system"""
    print("🔍 Testing Knowledge Base")
    print("=" * 50)
    
    # Test knowledge base file existence
    knowledge_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "raw", "processed", "Sarmaye maskan-compressed.md"
    )
    if os.path.exists(knowledge_file):
        print(f"✅ Knowledge base file found: {knowledge_file}")
        
        # Get file size
        file_size = os.path.getsize(knowledge_file) / 1024  # KB
        print(f"📄 File size: {file_size:.2f} KB")
    else:
        print(f"❌ Knowledge base file not found: {knowledge_file}")
        return False
    
    # Test KnowledgeRetriever initialization
    try:
        print("\n🔄 Initializing Knowledge Retriever...")
        retriever = KnowledgeRetriever(knowledge_file)
        print("✅ Knowledge Retriever initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Knowledge Retriever: {e}")
        return False
    
  
    # Test basic retrieval
    test_queries = [
        "تحلیل بازار مسکن",
        "housing market trends",
        "real estate investment",
        "economic factors affecting housing",
        "market cycles"
    ]
    
    print("\n🔍 Testing Knowledge Retrieval:")
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n  {i}. Query: '{query}'")
            result = retriever.retrieve_knowledge(query)
            
            if result and len(result) > 0:
                print(f"     ✅ Retrieved {len(result)} characters")
                # Show first 100 characters as preview
                preview = result[:100].replace('\n', ' ').strip()
                print(f"     📝 Preview: {preview}...")
            else:
                print(f"     ⚠️  No results returned")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Test full RAG pipeline
    print("\n🤖 Testing Full RAG Pipeline:")
    rag_test_queries = [
        "What are the main factors affecting housing prices?",
        "چه عواملی بر قیمت مسکن تأثیر می‌گذارند؟",
        "How do economic cycles impact real estate market?"
    ]
    
    for i, query in enumerate(rag_test_queries, 1):
        try:
            print(f"\n  {i}. Query: '{query}'")
            print("     🔄 Processing...")
            
            result = retriever.process_query(query, max_iterations=2)
            
            if result and 'answer' in result:
                print(f"     ✅ Answer generated ({result.get('iterations', 0)} iterations)")
                print(f"     📊 Source: {result.get('source', 'unknown')}")
                
                # Show answer preview
                answer_preview = result['answer'][:200].replace('\n', ' ').strip()
                print(f"     💬 Answer: {answer_preview}...")
                
            else:
                print(f"     ⚠️  No answer generated")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    print("\n🎉 Knowledge Base test completed!")
    return True

def test_vectorstore_stats():
    """Test and display vectorstore statistics"""
    print("\n📊 Vectorstore Statistics:")
    print("-" * 30)
    
    try:
        retriever = get_knowledge_retriever()
        
        if hasattr(retriever, 'vectorstore') and retriever.vectorstore:
            # Try to get some stats about the vectorstore
            vectorstore = retriever.vectorstore
            
            # Get retriever for testing
            retriever_tool = vectorstore.as_retriever(search_kwargs={"k": 1})
            test_docs = retriever_tool.get_relevant_documents("test query")
            
            print(f"✅ Vectorstore is operational")
            print(f"📄 Sample document length: {len(test_docs[0].page_content) if test_docs else 0} characters")
            
        else:
            print("❌ Vectorstore not available")
            
    except Exception as e:
        print(f"❌ Error getting vectorstore stats: {e}")

if __name__ == "__main__":
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found. Some tests may fail.")
    
    success = test_knowledge_base()
    print("\n" + "=" * 50)
    print("Test completed! Check the results above.") 