from langsmith import traceable
from langchain.tools import tool
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from src.configs.llm_config import get_llm
from ...models.state import RISAState
from ..utils.knowlge_base_deep_research.graph import get_knowledge_retriever
from .web_search import get_web_search_agent

@tool
def search_knowledge_base(query: str) -> str:
    """Search the real estate knowledge base for relevant information."""
    try:
        retriever = get_knowledge_retriever()
        result = retriever.process_query(query)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error searching knowledge base: {e}"

@tool 
def search_web(query: str) -> str:
    """Search the web for current real estate market information."""
    try:
        web_agent = get_web_search_agent()
        if web_agent.should_use_web_search(query):
            result = web_agent.process_web_query(query)
            return json.dumps(result, ensure_ascii=False)
        else:
            return "Web search not needed for this query"
    except Exception as e:
        return f"Error searching web: {e}"

class DataIngestAgent:
    """Enhanced data ingest agent with agentic RAG and web search capabilities"""
    
    def __init__(self):
        self.knowledge_retriever = get_knowledge_retriever()
        self.web_search_agent = get_web_search_agent()
        self.model = get_llm()
        
        # LangGraph-style tools
        self.tools = [search_knowledge_base, search_web]
        self.model_with_tools = self.model.bind_tools(self.tools)
        
        print("✅ Data ingest agent initialized successfully with LangGraph patterns")
    
    @traceable
    def process_query(self, state: RISAState) -> RISAState:
        """Enhanced data ingest using LangGraph-style tool calling"""
        print("📊 Enhanced Data Ingest Agent Starting...")
        
        query = state.get('user_query', '')
        if not query:
            print("❌ No user query provided")
            state['raw_data'] = {"error": "No query provided"}
            return state
        
        try:
            # Create LangGraph-style messages
            messages = [
                SystemMessage(content="""You are a real estate data analyst. You have access to:
                1. search_knowledge_base: For historical/theoretical real estate knowledge
                2. search_web: For current market information
                
                Analyze the user's query and gather comprehensive information from both sources.
                Always search the knowledge base first, then determine if web search is needed."""),
                HumanMessage(content=f"Analyze this real estate query: {query}")
            ]
            
            # Let the model decide which tools to use
            response = self.model_with_tools.invoke(messages)
            
            # Process any tool calls
            tool_results = {}
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    if tool_name == 'search_knowledge_base':
                        print("📚 Searching knowledge base...")
                        kb_result = search_knowledge_base.invoke(tool_args)
                        tool_results['knowledge_base'] = json.loads(kb_result) if kb_result.startswith('{') else kb_result
                    
                    elif tool_name == 'search_web':
                        print("🌐 Searching web...")
                        web_result = search_web.invoke(tool_args)
                        tool_results['web_search'] = json.loads(web_result) if web_result.startswith('{') else web_result
            
            # Synthesize results using LangGraph patterns
            synthesized_result = self._synthesize_with_langgraph(query, tool_results, response.content)
            
            # Update state with comprehensive data
            state['raw_data'] = {
                'query': query,
                'tool_results': tool_results,
                'agent_reasoning': response.content,
                'synthesized_analysis': synthesized_result,
                'tools_used': list(tool_results.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
            # Extract key facts for book_facts
            state['book_facts'] = self._extract_book_facts_langgraph(tool_results.get('knowledge_base', {}))
            
            print("✅ Enhanced data ingest completed with LangGraph patterns")
            print(f"   - Tools used: {list(tool_results.keys())}")
            
        except Exception as e:
            print(f"❌ Error in enhanced data ingest: {e}")
            state['raw_data'] = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            state['book_facts'] = {}
        
        return state

    @traceable
    def _synthesize_with_langgraph(self, query: str, tool_results: Dict[str, Any], agent_reasoning: str) -> Dict[str, Any]:
        """Synthesize results using LangGraph message-based patterns"""
        
        if not tool_results:
            return {
                'synthesized_answer': 'No information gathered from tools.',
                'confidence': 'low',
                'sources': []
            }
        
        # Create synthesis conversation
        synthesis_messages = [
            SystemMessage(content="""You are an expert real estate analyst. 
            Synthesize the tool results to provide a comprehensive answer.
            Distinguish between historical knowledge and current market data."""),
            HumanMessage(content=f"""
            Query: {query}
            
            Agent's initial reasoning: {agent_reasoning}
            
            Tool Results:
            {json.dumps(tool_results, ensure_ascii=False, indent=2)}
            
            Provide a comprehensive synthesis:
            """)
        ]
        
        try:
            response = self.model.invoke(synthesis_messages)
            
            return {
                'synthesized_answer': response.content.strip(),
                'confidence': 'high' if len(tool_results) > 1 else 'medium',
                'sources': list(tool_results.keys()),
                'synthesis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error synthesizing with LangGraph: {e}")
            return {
                'synthesized_answer': f'Error synthesizing information: {e}',
                'confidence': 'low',
                'sources': []
            }

    @traceable
    def _extract_book_facts_langgraph(self, knowledge_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key facts using LangGraph message patterns"""
        
        if not knowledge_result:
            return {}
        
        try:
            extraction_messages = [
                SystemMessage(content="""Extract key facts, statistics, and insights from Persian real estate content.
                Focus on market cycles, economic factors, government policies, and investment strategies.
                Return structured information."""),
                HumanMessage(content=f"Extract key facts from: {json.dumps(knowledge_result, ensure_ascii=False)}")
            ]
            
            response = self.model.invoke(extraction_messages)
            
            # Try to parse as structured data
            try:
                # Look for JSON in response
                content = response.content.strip()
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    facts = json.loads(content[start:end])
                else:
                    facts = {'extracted_content': content}
            except:
                facts = {
                    'extracted_content': response.content.strip(),
                    'source': 'knowledge_base',
                    'extraction_timestamp': datetime.now().isoformat()
                }
            
            return facts
            
        except Exception as e:
            print(f"❌ Error extracting book facts: {e}")
            return {
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def get_tools(self) -> List:
        """Get available tools for LangGraph integration"""
        return self.tools
    
    def as_langgraph_node(self):
        """Return a function suitable for use as a LangGraph node"""
        def node_function(state: Dict[str, Any]) -> Dict[str, Any]:
            # Convert dict state to RISAState for compatibility
            risa_state = RISAState(state)
            result_state = self.process_query(risa_state)
            return dict(result_state)
        return node_function

# Global instance
_data_ingest_agent = None

def get_data_ingest_agent() -> DataIngestAgent:
    """Get or create the global data ingest agent instance"""
    global _data_ingest_agent
    if _data_ingest_agent is None:
        _data_ingest_agent = DataIngestAgent()
    return _data_ingest_agent

# Backward compatibility function
@traceable
def data_ingest(state: RISAState) -> RISAState:
    """Backward compatibility wrapper for the DataIngestAgent"""
    agent = get_data_ingest_agent()
    return agent.process_query(state)
    