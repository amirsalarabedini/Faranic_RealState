"""
Market Analysis Agent - Web Data Expert for Real Estate Information
"""

import sys
import os
from typing import Dict, Any, List
import asyncio
import json

from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder, TaskType
from src.agents.core.agent_communication import AgentMessage

# Import the autonomous deep research agent and its configuration
from src.agents.utils.web_deep_research.web_graph import get_deep_research_agent
from src.agents.utils.web_deep_research.configuration import Configuration as WebResearchConfig
from src.agents.utils.web_deep_research.utils import get_today_str

class MarketAnalysisAgent(BaseAgent):
    """
    The Market Analysis Agent performs deep, autonomous web research on a given topic
    by leveraging the web_graph agent.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "MarketAnalysisAgent")
        self.deep_research_agent = get_deep_research_agent()
        self.log_activity("Field Researcher Initialized with Deep Research Graph")

    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
        """
        Processes a field research work request by invoking the deep web research graph.
        """
        task_value = work_order.primary_task.value if work_order.primary_task else "general_inquiry"
        self.log_activity("Processing deep research request", {"task": task_value})

        # Create a single, focused research topic from the work order
        location = "Iran"
        if work_order.property_specs and work_order.property_specs.location:
            location = work_order.property_specs.location
        elif work_order.key_information and work_order.key_information.get("location"):
            location = work_order.key_information.get("location")

        task_description = task_value.replace('_', ' ')
        topic = f"A comprehensive report on {task_description} for real estate in {location}"

        self.log_activity("Invoking Deep Research Graph", {"topic": topic})

        try:
            # Create a configuration object for the web research graph
            
            config = WebResearchConfig()
            
            # The web graph is autonomous and uses its own internal configuration.
            final_state = await self.deep_research_agent.ainvoke(
                {"topic": topic},
                config={"configurable": config}
            )
            
            report = final_state.get("final_report", "Failed to generate a report.")
            
            return {
                "agent_type": self.agent_type,
                "task_completed": "deep_web_research",
                "results": {
                    "location_researched": location,
                    "research_date": get_today_str(),
                    "report": report
                }
            }
        except Exception as e:
            self.log_activity("Error invoking Deep Research Graph", {"error": str(e)})
            return {
                "agent_type": self.agent_type,
                "task_completed": "deep_web_research",
                "results": { "error": f"An error occurred during deep research: {str(e)}" }
            }

    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the Market Analysis Agent."""
        return {
            "agent_type": "MarketAnalysisAgent",
            "primary_function": "Autonomous Deep Web Research",
            "capabilities": [
                "Generate multi-section research reports on a topic.",
                "Autonomously plan research, search the web, and write content.",
                "Reflect on and improve its own research sections.",
            ],
            "input_types": ["work_orders"],
            "output_types": ["comprehensive_research_reports"],
        } 