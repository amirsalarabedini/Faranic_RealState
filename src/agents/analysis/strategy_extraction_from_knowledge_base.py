"""
Investment Strategy Agent - Provides investment strategies from knowledge base
"""

import sys
import os
from typing import Dict, Any, List
import asyncio
from src.agents.utils.knowledge_base_deep_research.knowlge_base_graph import get_knowledge_agent
from src.agents.utils.knowledge_base_deep_research.configuration import Configuration as KnowledgeConfig
from src.agents.prompts import STRATEGY_EXTRACTION_FACTS_PROMPT, STRATEGY_EXTRACTION_METHODS_PROMPT


"""
The Strategy Extraction Agent uses the autonomous knowledge base graph to provide
investment strategies, market principles, and high-level advice by extracting and
synthesizing key facts and methods.
"""

async def extract_investment_strategies(work_order: Dict[str, Any]) -> str:
    """
    Extracts investment strategies from the knowledge base based on the work order.
    """
    client_type = work_order.get("client_type")
    task = work_order.get("primary_task")
    location = work_order.get("key_information", {}).get("location")

    if not all([client_type, task, location]):
        return "Could not extract investment strategies due to missing information in the work order."

    # Initialize the knowledge agent graph
    knowledge_agent_graph = get_knowledge_agent()
    
    # Create a configuration dictionary
    config = {
        "configurable": {
            "llm_provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.1,
            "retrieval_limit": 5,
            "max_iterations": 3
        }
    }

    # 1. Extract key facts and principles
    facts_prompt = STRATEGY_EXTRACTION_FACTS_PROMPT.format(
        client_type=client_type, task=task, location=location
    )
    key_facts_result = await knowledge_agent_graph.ainvoke(
        {"query": facts_prompt}, config=config
    )
    print(key_facts_result)
    key_facts = key_facts_result.get("answer", "No facts found.")


    # 2. Extract specific methods and strategies
    methods_prompt = STRATEGY_EXTRACTION_METHODS_PROMPT.format(
        client_type=client_type, task=task, location=location
    )
    investment_methods_result = await knowledge_agent_graph.ainvoke(
        {"query": methods_prompt}, config=config
    )
    investment_methods = investment_methods_result.get("answer", "No methods found.")

    # 3. Synthesize the advice
    advice = f"""
    **Key Market Principles for {client_type} in {location}**:
    {key_facts}

    **Recommended Investment Strategies & Methods**:
    {investment_methods}
    """
    return advice.strip()