"""
Main Orchestrator for the Faranic Real Estate Multi-Agent System
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from src.agents.specialists.query_understanding_agent import run_query_understanding_agent
from src.agents.specialists.strategic_advisor import run_strategic_advisor
from src.agents.specialists.generate_report_agent import run_generate_report_agent, format_strategic_advice

# Ensure all necessary paths are set up
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def main(user_query: str, report_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """
    Main function to orchestrate the multi-agent workflow, yielding results as they are generated.
    """
    yield "### Starting Faranic Real Estate Agent Workflow...\n"

    # 1. Understand the user's query and create a work order
    yield f"\n**Orchestrator:** Understanding user query: '{user_query}'\n"
    work_order = run_query_understanding_agent(user_query)
    work_order_md = f"#### ✅ Work Order Created\n```json\n{json.dumps(work_order, indent=2)}\n```"
    yield work_order_md

    # 2. Define the report date
    if report_date is None:
        report_date = datetime.now().strftime("%B %d, %Y")
        yield f"\n**Orchestrator:** Using current date: {report_date}\n"
    
    # 3. Run the Strategic Advisor to get comprehensive advice
    yield "\n---\n### Running Strategic Advisor...\n"
    strategic_advice = await run_strategic_advisor(work_order, report_date)

    if "error" in strategic_advice:
        error_md = f"**Orchestrator:** Halting workflow due to error from Strategic Advisor: {strategic_advice['error']}"
        yield error_md
        return

    formatted_advice_for_stream = format_strategic_advice(strategic_advice)
    advice_md = f"#### ✅ Strategic Advice Received\n{formatted_advice_for_stream}"
    yield advice_md

    # 4. Run the Generate Report Agent to create the final output
    yield "\n---\n### Generating Final Report...\n"
    final_report = await run_generate_report_agent(work_order, strategic_advice)
    
    yield "\n---\n## Final Investment Report\n"
    yield final_report

    yield "\n\n---\n#### ✅ Faranic Real Estate Agent Workflow Complete ---"


if __name__ == "__main__":
    async def stream_test():
        # Example user query
        query = "عوامل کلیدی و تعیین‌کننده در شروع و پایان هر یک از اپیزودهای رونق شدید، رونق اندک، رکود اندک، رکود شدید و چرخش بازار کدامند؟"
        
        print("--- Running Main Orchestrator in Streaming Mode ---")
        async for report_chunk in main(query, report_date="21 - 3 - 2013, 21 - 3 - 2014"):
            print(report_chunk)

    asyncio.run(stream_test()) 