"""
Field Researcher Agent - Web Data Expert for Real Estate Information, now using LangGraph.
"""

import sys
import os

# Add the project root to the Python path to enable direct script execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Dict, Any, List
import asyncio
import json

from src.agents.core import BaseAgent, AgentState, WorkOrder, TaskType, ClientType
from langchain_core.messages import HumanMessage

# Import the autonomous deep research agent and its configuration
from src.agents.utils.web_deep_research.web_graph import get_deep_research_agent
from src.agents.utils.web_deep_research.configuration import Configuration as WebResearchConfig
from src.agents.utils.web_deep_research.utils import get_today_str
from src.agents.prompts import FIELD_RESEARCHER_EXTRACTION_PROMPT, FIELD_RESEARCHER_TREND_SUMMARY_PROMPT



class FieldResearcherAgent(BaseAgent):
    """
    The Field Researcher Agent performs deep, autonomous web research on a given topic
    by leveraging the web_graph agent, built on the LangGraph framework.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "FieldResearcherAgent")
        self.deep_research_agent = get_deep_research_agent()
        self._log_activity("Field Researcher Initialized with Deep Research Graph")

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Returns a dictionary of the agent's capabilities.
        """
        return {
            "name": self.agent_type,
            "tasks": [
                {
                    "task_type": TaskType.DEEP_DIVE_RESEARCH.name,
                    "description": "Performs in-depth web research on a given topic and returns a structured report.",
                    "parameters": {
                        "query": "The research topic or question."
                    }
                },
                {
                    "task_type": TaskType.TREND_ANALYSIS.name,
                    "description": "Analyzes market or topic trends based on web research and returns a summary.",
                    "parameters": {
                        "query": "The topic for trend analysis."
                    }
                }
            ],
            "description": "An autonomous agent that specializes in deep web research to extract information and identify trends."
        }

    def _can_handle_task(self, work_order: WorkOrder) -> bool:
        """
        Check if this agent can handle the given work order's primary task.
        """
        return work_order.primary_task in [TaskType.DEEP_DIVE_RESEARCH, TaskType.TREND_ANALYSIS]

    async def get_llm_response(self, prompt: str) -> str:
        """
        Helper function to get a response from the configured LLM.
        """
        self._log_activity("Invoking LLM for response generation.")
        response = await self.llm.ainvoke(prompt)
        return response.content

    async def process_work_request(self, work_order: WorkOrder, state: AgentState) -> Dict[str, Any]:
        """
        Processes a work request based on the task type. This method is called by the BaseAgent's workflow.
        """
        self._log_activity(f"Processing work request with task type: {work_order.primary_task.name}")

        if work_order.primary_task == TaskType.DEEP_DIVE_RESEARCH:
            return await self._perform_deep_dive_research(work_order)
        elif work_order.primary_task == TaskType.TREND_ANALYSIS:
            return await self._analyze_trends(work_order)
        else:
            # This case should ideally not be reached due to `_can_handle_task` validation
            error_msg = f"Unknown task type: {work_order.primary_task.name}"
            self._log_activity(error_msg, details={"level": "error"})
            return {"error": error_msg}

    async def _perform_deep_dive_research(self, work_order: WorkOrder) -> Dict[str, Any]:
        """
        Performs a deep dive research on a given query, extracts key information,
        and returns it as structured data.
        """
        research_query = work_order.processed_query
        if not research_query:
            return {"error": "No research query provided for deep dive."}

        self._log_activity(f"Starting deep dive research for: '{research_query}'")
        
        research_result = await self._run_deep_research(research_query)
        if isinstance(research_result, dict) and "error" in research_result:
            return research_result

        research_report = research_result

        self._log_activity("Deep dive research complete. Extracting key information.")
        extraction_prompt = FIELD_RESEARCHER_EXTRACTION_PROMPT.format(
            research_report=research_report,
            research_query=research_query
        )

        llm_response_str = ""
        try:
            llm_response_str = await self.get_llm_response(extraction_prompt)
            # Find the JSON part of the response, resilient to markdown code blocks
            json_start = llm_response_str.find('{')
            json_end = llm_response_str.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in the response.")
            json_part = llm_response_str[json_start:json_end]
            extracted_data = json.loads(json_part)
            self._log_activity("Successfully extracted and parsed structured data.")
            return {"status": "success", "data": extracted_data}
        except (json.JSONDecodeError, ValueError) as e:
            error_msg = f"Failed to parse extracted data as JSON. Error: {e}"
            self._log_activity(error_msg, details={"level": "error"})
            return {"error": error_msg, "raw_data": llm_response_str}

    async def _analyze_trends(self, work_order: WorkOrder) -> Dict[str, Any]:
        """
        Analyzes trends based on a research query. It performs research and then
        summarizes the findings to identify trends.
        """
        research_query = work_order.processed_query
        if not research_query:
            return {"error": "No research query provided for trend analysis."}

        self._log_activity(f"Starting trend analysis for: '{research_query}'")

        research_result = await self._run_deep_research(research_query)
        if isinstance(research_result, dict) and "error" in research_result:
            return research_result

        research_report = research_result
        
        self._log_activity("Trend research complete. Summarizing trends.")
        summary_prompt = FIELD_RESEARCHER_TREND_SUMMARY_PROMPT.format(
            research_report=research_report,
            research_query=research_query
        )
        
        trend_summary = await self.get_llm_response(summary_prompt)
        self._log_activity("Trend summarization complete.")
        return {"status": "success", "summary": trend_summary}

    async def _run_deep_research(self, research_query: str) -> str | Dict[str, Any]:
        """
        A helper function to run the deep research agent and get the final report.
        Returns the report as a string or an error dictionary.
        """
        self._log_activity(f"Invoking deep research for query: {research_query}")
        config = {
            "configurable": {
                "thread_id": f"research_{get_today_str()}",
                "research_topic": research_query,
            }
        }
        
        # The input to the stream should be a dictionary, often with a 'messages' key.
        initial_input = {"messages": [HumanMessage(content=research_query)]}
        
        final_report = ""
        try:
            # The deep research agent streams back events. We process them to find the final report.
            for event in self.deep_research_agent.stream(initial_input, config=config):
                if "messages" in event:
                    # The final report is typically the last message in the stream.
                    message = event["messages"][-1]
                    if message.content:
                        final_report = message.content
            
            if not final_report:
                msg = "Deep research did not produce a final report."
                self._log_activity(msg, details={"level": "error"})
                return {"error": msg}

            self._log_activity("Successfully received final report from deep research.")
            return final_report
        except Exception as e:
            error_msg = f"An error occurred during deep research: {e}"
            self._log_activity(error_msg, details={"level": "error"})
            return {"error": error_msg}

if __name__ == '__main__':
    async def run_field_researcher():
        """
        An asynchronous function to run the FieldResearcherAgent for demonstration.
        """
        agent = FieldResearcherAgent("researcher_007")

        # Create a dummy work order for a deep dive research task
        work_order = WorkOrder(
            order_id="order_123",
            client_type=ClientType.RESEARCHER,
            client_persona="A data scientist researching real estate for a personal project.",
            primary_task=TaskType.DEEP_DIVE_RESEARCH,
            raw_query="What are the current market trends for residential real estate in Austin, TX?",
            processed_query="Current market trends for residential real estate in Austin, TX"
        )
        
        print(f"Running Field Researcher for: '{work_order.processed_query}'")
        # Use the new process_work_order method which invokes the LangGraph workflow
        result = await agent.process_work_order(work_order)
        
        print("\n--- Research Result ---")
        # The final result from `process_work_request` is in the `results` key of the final state
        print(json.dumps(result.get("results", {}), indent=4))
        print("---------------------\n")

        # You can also inspect the final state
        print("\n--- Final Workflow State ---")
        print(f"Status: {result.get('status')}")
        print(f"Error: {result.get('error')}")
        print("--------------------------\n")

    # To run the async function, we need an event loop
    try:
        asyncio.run(run_field_researcher())
    except KeyboardInterrupt:
        print("Field Researcher run interrupted.")
    except Exception as e:
        print(f"An error occurred: {e}")
     