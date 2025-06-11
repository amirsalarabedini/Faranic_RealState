"""
Orchestrator - Manages workflow execution and agent coordination.
"""
from typing import Dict, Any
from src.agents.core.agent_communication import AgentMessage
from src.agents.core.work_order import WorkOrder

class Orchestrator:
    """
    The Orchestrator is responsible for managing the overall workflow,
    routing tasks to the appropriate agents, and ensuring the successful
    completion of the user's request.
    """
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        # A simple logger for now
        print("Orchestrator Initialized")
        print(f"Loaded agents: {list(self.agents.keys())}")

    async def execute_workflow(self, initial_work_order: WorkOrder) -> Dict[str, Any]:
        """
        Execute the main analysis workflow.
        """
        print(f"Starting workflow for order: {initial_work_order.order_id}")

        # This is a placeholder for a simple, linear workflow.
        # A real orchestrator would have a more complex routing logic.

        # 1. (Pretend) The work order is already created by the QueryUnderstandingAgent.
        
        # 2. Field research / Market Analysis
        market_analysis_agent = self.agents.get("MarketAnalysisAgent")
        if market_analysis_agent:
            print("Dispatching to MarketAnalysisAgent")
            market_analysis_results = await market_analysis_agent.process_work_request(
                initial_work_order,
                AgentMessage(
                    sender_agent="Orchestrator",
                    recipient_agent=market_analysis_agent.agent_id,
                    message_type="work_request",
                    subject=f"Market analysis for {initial_work_order.property_specs.location if initial_work_order.property_specs else 'general inquiry'}",
                    content={}
                )
            )
            print("Received results from MarketAnalysisAgent")
        else:
            market_analysis_results = {"error": "MarketAnalysisAgent not found"}

        # 3. Generate Report
        generate_report_agent = self.agents.get("GenerateReportAgent")
        if generate_report_agent:
            print("Dispatching to GenerateReportAgent")
            final_report = await generate_report_agent.process_work_request(
                initial_work_order,
                AgentMessage(
                    sender_agent="Orchestrator",
                    recipient_agent=generate_report_agent.agent_id,
                    message_type="report_generation_request",
                    subject=f"Final report for query: {initial_work_order.raw_query}",
                    content={
                        "findings": [
                            market_analysis_results
                        ]
                    }
                )
            )
            print("Received final report")
        else:
            final_report = {"error": "GenerateReportAgent not found"}

        return final_report 