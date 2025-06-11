"""
The Generate Report Agent is responsible for creating the final analysis report.
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
        Processes a work order to generate a final report by synthesizing
        findings from other agents.
        """
        self.log_activity(
            "Starting report generation.",
            {"order_id": work_order.order_id, "query": work_order.raw_query}
        )

        findings = request_message.content.get("findings", [])

        if not findings:
            self.log_activity("No findings provided to generate report.", {"order_id": work_order.order_id})
            report = {
                "title": f"Analysis Report for query: {work_order.raw_query}",
                "summary": "No findings were provided for this query.",
                "sections": []
            }
        else:
            report = self._generate_report_from_findings(work_order.raw_query, findings)

        self.log_activity("Report generation complete.", {"order_id": work_order.order_id})
        
        return {
            "agent_type": self.agent_type,
            "task_completed": "report_generation",
            "report": report
        }

    def _generate_report_from_findings(self, query: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a structured report from a list of findings.

        This method assumes that each finding is a dictionary, potentially
        containing keys like 'agent_type', 'task_completed', and 'result'.
        The 'result' dictionary may contain a 'summary' for the executive summary.
        """
        title = f"Comprehensive Analysis Report for: '{query}'"
        
        # Synthesize a summary from all findings
        summary_parts = []
        for finding in findings:
            # Assuming the summary is located in finding['result']['summary']
            if isinstance(finding, dict):
                result = finding.get("result", {})
                if isinstance(result, dict) and "summary" in result:
                    summary_parts.append(str(result["summary"]))

        if summary_parts:
            executive_summary = " ".join(summary_parts)
        else:
            executive_summary = "An executive summary could not be generated from the provided findings."

        # Structure the findings into report sections
        report_sections = []
        for i, finding in enumerate(findings):
            if isinstance(finding, dict):
                agent_type = finding.get("agent_type", "Unknown Agent")
                task = finding.get("task_completed", "undisclosed task")
                
                # We will use the 'result' key if present, otherwise, the whole finding.
                content = finding.get("result", finding)
                
                section = {
                    "section_title": f"Analysis by {agent_type} for {task}",
                    "content": content
                }
                report_sections.append(section)
            else:
                # Handle cases where a finding is not a dictionary
                report_sections.append({
                    "section_title": f"Finding #{i + 1}",
                    "content": str(finding)
                })

        return {
            "title": title,
            "summary": executive_summary,
            "sections": report_sections
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