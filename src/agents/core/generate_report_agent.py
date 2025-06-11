"""
Generate Report Agent - Creates the final analysis report.
"""

from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder
from src.agents.core.agent_communication import AgentMessage
from typing import Dict, Any, List

class GenerateReportAgent(BaseAgent):
    """
    The Generate Report Agent synthesizes findings from all other agents
    into a comprehensive and well-structured final report.
    """
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "GenerateReportAgent")

    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
        """
        Process a report generation request.
        """
        # This is a placeholder implementation.
        self.log_activity("Processing report generation work order", {"order_id": work_order.order_id})
        
        # In a real implementation, this agent would receive a list of findings
        # from other agents.
        findings = request_message.content.get("findings", [])
        
        return {
            "agent_type": self.agent_type,
            "task_completed": "report_generation",
            "report": {
                "title": f"Analysis Report for query: {work_order.raw_query}",
                "summary": "This is a placeholder summary.",
                "sections": findings
            }
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return the capabilities of the Generate Report Agent.
        """
        return {
            "agent_type": "GenerateReportAgent",
            "primary_function": "Final report generation",
            "capabilities": [
                "Synthesize findings from multiple agents.",
                "Structure information into a coherent report.",
                "Format the report in various formats (e.g., PDF, markdown)."
            ],
            "input_types": ["list_of_agent_findings"],
            "output_types": ["final_report"]
        } 