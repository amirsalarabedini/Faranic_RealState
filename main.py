"""
Main Orchestrator for the Faranic Real Estate Multi-Agent System
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.specialists.query_understanding_agent import run_query_understanding_agent
from src.agents.specialists.strategic_advisor import run_strategic_advisor
from src.agents.specialists.generate_report_agent import run_generate_report_agent

# Ensure all necessary paths are set up
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def main(user_query: str, report_date: Optional[str] = None):
    """
    Main function to orchestrate the multi-agent workflow.
    If no report_date is provided, the current date will be used.
    """
    print("--- Starting Faranic Real Estate Agent Workflow ---")

    # 1. Understand the user's query and create a work order
    print(f"Orchestrator: Understanding user query: '{user_query}'")
    work_order = run_query_understanding_agent(user_query)
    print(f"Orchestrator: Work order created: {json.dumps(work_order, indent=2)}")

    # 2. Define the report date
    if report_date is None:
        report_date = datetime.now().strftime("%B %d, %Y")
        print(f"Orchestrator: No report date provided. Using current date: {report_date}")
    
    # 3. Run the Strategic Advisor to get comprehensive advice
    # This agent orchestrates its own research and knowledge base extraction
    strategic_advice = await run_strategic_advisor(work_order, report_date)

    if "error" in strategic_advice:
        print(f"Orchestrator: Halting workflow due to error from Strategic Advisor: {strategic_advice['error']}")
        return

    print("Orchestrator: Strategic advice received. Generating final report...")

    # 4. Run the Generate Report Agent to create the final output
    final_report = await run_generate_report_agent(work_order, strategic_advice)

    # 5. Save the final report
    report_path = "final_investment_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"--- Faranic Real Estate Agent Workflow Complete ---")
    print(f"Final report saved to: {report_path}")
    print("\n--- Final Report Preview ---")
    print(final_report) # Print a preview

if __name__ == "__main__":
    # Example user query
    query = "عوامل کلیدی و تعیین‌کننده در شروع و پایان هر یک از اپیزودهای رونق شدید، رونق اندک، رکود اندک، رکود شدید و چرخش بازار کدامند؟"

    # To run with a specific date, uncomment the following line:
    # asyncio.run(main(query, report_date="October 31, 2023"))

    # To run with the current date, use this line:
    asyncio.run(main(query, report_date="21 - 3 - 2013, 21 - 3 - 2014")) 