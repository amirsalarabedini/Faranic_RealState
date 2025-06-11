"""
Investment Strategy Agent - Provides investment strategies from knowledge base
"""

import sys
import os
from typing import Dict, Any, List
import asyncio

from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder, TaskType
from src.agents.core.agent_communication import AgentMessage
from src.agents.utils.knowledge_base_deep_research.knowlge_base_graph import get_knowledge_agent
from src.agents.utils.knowledge_base_deep_research.configuration import Configuration as KnowledgeConfig
from src.agents.prompts import STRATEGY_EXTRACTION_FACTS_PROMPT, STRATEGY_EXTRACTION_METHODS_PROMPT


class Strategy_Extraction_From_Knowledge_Base(BaseAgent):
    """
    The Strategy Extraction Agent uses the autonomous knowledge base graph to provide
    investment strategies, market principles, and high-level advice by extracting and
    synthesizing key facts and methods.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "Strategy_Extraction_From_Knowledge_Base")
        self.knowledge_agent = get_knowledge_agent()
        self.log_activity("Strategy Extraction Agent Initialized with Knowledge Graph")

    async def get_strategic_advice(self, work_order: WorkOrder) -> Dict[str, Any]:
        """
        Query the knowledge base for investment strategies, extracting key facts and methods.
        """
        location = work_order.property_specs.location if work_order.property_specs else 'Iran'
        client_type = work_order.client_type.value
        task = work_order.primary_task.value

        fact_query = STRATEGY_EXTRACTION_FACTS_PROMPT.format(
            client_type=client_type,
            task=task
        )
        method_query = STRATEGY_EXTRACTION_METHODS_PROMPT.format(
            client_type=client_type,
            task=task,
            location=location
        )

        queries = {
            "facts": fact_query,
            "methods": method_query
        }
        
        self.log_activity("Invoking Knowledge Graph with multi-faceted query", {"queries": queries})
        
        try:
            # Concurrently query for facts and methods
            fact_task = self.knowledge_agent.ainvoke({"query": queries["facts"]})
            method_task = self.knowledge_agent.ainvoke({"query": queries["methods"]})
            
            results = await asyncio.gather(fact_task, method_task)
            
            facts_result = results[0].get("answer", "No relevant facts were found in the knowledge base.")
            methods_result = results[1].get("answer", "No specific methods were found in the knowledge base.")
            
            # Synthesize the advice
            no_facts = "No definitive answer" in facts_result or "No relevant facts" in facts_result
            no_methods = "No definitive answer" in methods_result or "No specific methods" in methods_result

            if no_facts and no_methods:
                advice = "No definitive answer was found in the knowledge base for the given query."
                confidence = "low"
            else:
                advice = f"### Key Facts and Principles:\n{facts_result}\n\n### Recommended Methods and Strategies:\n{methods_result}"
                confidence = "high"

            return {
                "advice": advice,
                "source": "Internal Knowledge Base Graph (Synthesized)",
                "confidence": confidence
            }
        except Exception as e:
            self.log_activity("Error invoking Knowledge Graph", {"error": str(e)})
            return {
                "advice": f"An error occurred while consulting the knowledge base: {str(e)}",
                "source": "Internal Knowledge Base Graph",
                "confidence": "error"
            }
    
    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
        """
        Process a work request for strategic advice.
        """
        self.log_activity("Processing strategic advice request", {"order_id": work_order.order_id})
        
        advice_data = await self.get_strategic_advice(work_order)
        
        return {
            "agent_type": self.agent_type,
            "task_completed": "strategic_advice",
            "results": advice_data
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return a description of what this agent can do.
        """
        return {
            "agent_type": "InvestmentStrategyAgent",
            "primary_function": "Autonomous Knowledge-Based Advice",
            "capabilities": [
                "Provide investment strategies using an autonomous RAG system.",
                "Answer high-level questions about the real estate market.",
                "Leverage FAISS vectorstore and a self-correcting graph.",
            ],
            "input_types": ["work_orders"],
            "output_types": ["strategic_advice_reports"]
        } 
    
