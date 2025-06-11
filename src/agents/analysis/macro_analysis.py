"""
Macro Analysis Agent - Analyzes macroeconomic factors affecting real estate.
"""

from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder
from src.agents.core.agent_communication import AgentMessage
from typing import Dict, Any

class MacroAnalysisAgent(BaseAgent):
    """
    The Macro Analysis Agent assesses the impact of macroeconomic trends
    on the real estate market.
    """
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "MacroAnalysisAgent")

    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
        """
        Process a macro analysis request.
        """
        # This is a placeholder implementation.
        self.log_activity("Processing macro analysis work order", {"order_id": work_order.order_id})
        return {
            "agent_type": self.agent_type,
            "task_completed": "macro_analysis",
            "findings": "placeholder - e.g., rising interest rates may cool the market"
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return the capabilities of the Macro Analysis Agent.
        """
        return {
            "agent_type": "MacroAnalysisAgent",
            "primary_function": "Macroeconomic analysis for real estate",
            "capabilities": [
                "Analyze interest rates, GDP, and employment data.",
                "Assess the impact of economic policy on real estate.",
                "Provide a macroeconomic outlook for the market."
            ],
            "input_types": ["economic_data"],
            "output_types": ["macro_analysis_report"]
        } 