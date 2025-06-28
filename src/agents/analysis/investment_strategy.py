"""
Investment Strategy Agent - Provides investment strategies from knowledge base
"""

import sys
import os
from typing import Dict, Any, List
import asyncio


# Import your existing knowledge base utilities
from src.agents.utils.knowledge_base_deep_research.knowlge_base_graph import get_knowledge_agent
from src.agents.utils.knowledge_base_deep_research.configuration import Configuration as KnowledgeConfig


"""
The Investment Strategy Agent uses the autonomous knowledge base graph to provide
investment strategies, market principles, and high-level advice.
"""
    
