"""
Rental Market Analysis Agent - Analyzes rental market trends.
"""

from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder
from src.agents.core.agent_communication import AgentMessage
from typing import Dict, Any

class RentalMarketAnalysisAgent(BaseAgent):
    """
    The Rental Market Analysis Agent provides insights into the rental market,
    including trends, yields, and demand.
    """
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "RentalMarketAnalysisAgent")

    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
        """
        Process a rental market analysis request.
        """
        # This is a placeholder implementation.
        self.log_activity("Processing rental market analysis work order", {"order_id": work_order.order_id})
        return {
            "agent_type": self.agent_type,
            "task_completed": "rental_market_analysis",
            "findings": "placeholder - e.g., rental yields are compressing in the area"
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return the capabilities of the Rental Market Analysis Agent.
        """
        return {
            "agent_type": "RentalMarketAnalysisAgent",
            "primary_function": "Rental market analysis",
            "capabilities": [
                "Analyze rental prices and yields.",
                "Assess rental demand and vacancy rates.",
                "Provide insights for buy-to-let investors."
            ],
            "input_types": ["rental_listings_data", "demographic_data"],
            "output_types": ["rental_market_report"]
        } 