"""
The Generate Report Agent is responsible for creating the final analysis report.
"""
import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.configs.llm_config import get_default_llm
from src.agents.prompts import FINAL_REPORT_PROMPT
from langchain_core.messages import HumanMessage

def format_strategic_advice(advice: Dict[str, Any]) -> str:
    """Formats the structured strategic advice into a readable markdown string."""
    markdown_sections = []
    
    if "market_overview" in advice:
        markdown_sections.append(f"### Market Overview\n{advice['market_overview']}")
    
    if "key_opportunities" in advice and advice["key_opportunities"]:
        opportunities = "\n".join([f"- {item}" for item in advice["key_opportunities"]])
        markdown_sections.append(f"### Key Opportunities\n{opportunities}")
        
    if "potential_risks" in advice and advice["potential_risks"]:
        risks = "\n".join([f"- {item}" for item in advice["potential_risks"]])
        markdown_sections.append(f"### Potential Risks\n{risks}")

    if "recommended_strategy" in advice and advice["recommended_strategy"]:
        strategy = "\n".join([f"- {item}" for item in advice["recommended_strategy"]])
        markdown_sections.append(f"### Recommended Strategy\n{strategy}")

    if "success_metrics" in advice and advice["success_metrics"]:
        metrics = "\n".join([f"- {item}" for item in advice["success_metrics"]])
        markdown_sections.append(f"### Success Metrics\n{metrics}")
        
    return "\n\n".join(markdown_sections)

async def run_generate_report_agent(work_order: Dict[str, Any], strategic_advice: Dict[str, Any]) -> str:
    """
    The Generate Report Agent synthesizes findings from all other agents
    into a comprehensive and well-structured final report.
    """
    print("---Running Generate Report Agent---")
    
    llm = get_default_llm()
    
    # Format the structured advice into a readable string
    formatted_advice = format_strategic_advice(strategic_advice)
    
    # Format the prompt with the work order and formatted strategic advice
    prompt = FINAL_REPORT_PROMPT.format(
        work_order=json.dumps(work_order, indent=2),
        strategic_advice=formatted_advice
    )
    
    messages = [HumanMessage(content=prompt)]
    
    # Invoke the LLM to generate the report
    llm_response = await llm.ainvoke(messages)
    
    # The response should be the report string
    report = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
    
    print("---Generate Report Agent Finished---")
    return report

if __name__ == '__main__':
    async def main():
        # Mock data for testing
        mock_work_order = {
            "client_type": "investor",
            "primary_task": "investment_strategy",
            "key_information": {
                "location": "Tehran, Iran",
                "budget": "500,000",
                "property_type": "apartment"
            }
        }
        
        # Load the results from the strategic advisor to test the report generator
        with open("strategic_advisor_result.json", "r") as f:
            mock_strategic_advice = json.load(f)
            
        final_report = await run_generate_report_agent(mock_work_order, mock_strategic_advice)
        
        print("\n\n--- Final Report ---")
        print(final_report)
        
        # Save the report to a file
        with open("final_report.md", "w") as f:
            f.write(final_report)

    asyncio.run(main())