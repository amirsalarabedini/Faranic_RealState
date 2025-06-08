"""
Core RISA Agents
Essential agents for basic functionality with LangGraph integration
"""

from .data_ingest import data_ingest, get_data_ingest_agent, DataIngestAgent
from .market_cycle import market_cycle, get_market_cycle_agent, MarketCycleAgent
from .query_understanding import query_understanding, get_query_understanding_agent, QueryUnderstandingAgent
from .generate_report import generate_report, get_generate_report_agent, GenerateReportAgent
from .knowledge_retriever import get_knowledge_retriever, KnowledgeRetriever
from .web_search import get_web_search_agent, create_web_search_agent as WebSearchAgent


__all__ = [
    # Backward compatibility functions
    'data_ingest',
    'market_cycle',
    'query_understanding',
    'generate_report',
    
    # Factory functions (recommended pattern)
    'get_data_ingest_agent',
    'get_market_cycle_agent',
    'get_query_understanding_agent',
    'get_generate_report_agent',
    'get_knowledge_retriever',
    'get_web_search_agent',

    # Agent classes
    'DataIngestAgent',
    'MarketCycleAgent',
    'QueryUnderstandingAgent',
    'GenerateReportAgent',
    'KnowledgeRetriever',
    'WebSearchAgent'
]