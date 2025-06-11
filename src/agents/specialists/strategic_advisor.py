"""
Investment Strategy Agent - Provides investment strategies from knowledge base
"""

import sys
import os
from typing import Dict, Any, List
import asyncio

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder, TaskType
from src.agents.core.agent_communication import AgentMessage

# Import your existing knowledge base utilities
from src.agents.utils.knowledge_base_deep_research.knowlge_base_graph import get_knowledge_agent
from src.agents.utils.knowledge_base_deep_research.configuration import Configuration as KnowledgeConfig

class InvestmentStrategyAgent(BaseAgent):
    """
    The Investment Strategy Agent uses the autonomous knowledge base graph to provide
    investment strategies, market principles, and high-level advice.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "InvestmentStrategyAgent")
        self.knowledge_agent = get_knowledge_agent()
        self.log_activity("Strategic Advisor Initialized with Knowledge Graph")

    async def get_strategic_advice(self, work_order: WorkOrder) -> Dict[str, Any]:
        """
        Query the knowledge base for strategic advice using the knowledge graph.
        """
        query = f"Based on our internal knowledge, what is the best investment strategy for a {work_order.client_type.value} client regarding {work_order.primary_task.value} for a property in {work_order.property_specs.location if work_order.property_specs else 'Iran'}?"
        
        self.log_activity("Invoking Knowledge Graph", {"query": query})
        
        try:
            # The knowledge graph is autonomous and uses its own internal configuration.
            final_state = await self.knowledge_agent.ainvoke({"query": query})
            
            advice = final_state.get("answer", "No definitive answer was found in the knowledge base.")
            
            return {
                "advice": advice,
                "source": "Internal Knowledge Base Graph",
                "confidence": "high" if "No definitive answer" not in advice else "low"
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