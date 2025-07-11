"""
Strategic Advisor Agent - Expert in Real Estate Investment Strategy
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.configs.llm_config import get_default_llm
from src.agents.prompts import CHIEF_STRATEGIST_ADVICE_PROMPT, CHIEF_STRATEGIST_ADVICE_PROMPT_PERSIAN
from src.agents.specialists.models.strategic_advisor_models import StrategicAdvice
from src.agents.analysis.field_researcher import run_field_researcher
from src.agents.analysis.strategy_extraction_from_knowledge_base import extract_investment_strategies
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser

async def run_strategic_advisor(work_order: Dict[str, Any], report_date: Optional[str] = None, language: str = "English") -> Dict[str, Any]:
    """
    Runs the strategic advisor agent, which orchestrates field research and knowledge base
    extraction to generate comprehensive investment advice.

    Args:
        work_order: The client's work order with their profile and request.
        report_date: The date to be used for all research and reporting. Defaults to current date if None.
        language: The language to use for the advice prompt. Defaults to "English".

    Returns:
        A dictionary containing the strategic advice.
    """
    print("---Running Strategic Advisor---")

    llm = get_default_llm()
    parser = JsonOutputParser(pydantic_object=StrategicAdvice)

    # If no date is provided, default to the current date
    if report_date is None:
        report_date = datetime.now().strftime("%B %d, %Y")

    # 1. Run Field Researcher to get up-to-date market info
    property_specs = work_order.get('property_specs', {})
    property_details = ", ".join([f"{key.replace('_', ' ')}: {value}" for key, value in property_specs.items() if value])

    research_topic = (
        f"Real estate investment strategy for a {work_order.get('client_type')} in "
        f"{work_order.get('key_information', {}).get('location')} focusing on {work_order.get('primary_task')}. "
        f"Property details: {property_details}"
    )
    research_findings = await run_field_researcher(research_topic, report_date)
    print(f"---Strategic Advisor: Research findings received: {research_findings}---")

    # 2. Extract strategies from the internal knowledge base
    knowledge_base_strategies = await extract_investment_strategies(work_order)
    print(f"---Strategic Advisor: Knowledge base strategies received: {knowledge_base_strategies}---")

    # 3. Prepare the inputs for the final synthesis prompt
    client_profile = json.dumps(work_order, indent=2)
    market_analysis_summary = research_findings.get("summary", "No summary available.")
    
    # Ensure structured_data is always a dictionary before dumping
    structured_data_to_dump = research_findings.get("structured_data", {})
    if not isinstance(structured_data_to_dump, dict):
        print(f"---Strategic Advisor: WARNING: structured_data is not a dictionary. Type: {type(structured_data_to_dump)}. Attempting to convert.---")
        try:
            structured_data_to_dump = structured_data_to_dump.model_dump() # For Pydantic models
        except AttributeError:
            # If it's not a Pydantic model and not a dict, default to empty dict
            structured_data_to_dump = {}

    key_market_data = json.dumps(structured_data_to_dump, indent=2)
    print(f"---Strategic Advisor: Key market data (JSON dumped structured_data): {key_market_data}---")

    # 4. Generate comprehensive advice using the synthesis prompt
    if language == "Persian":
        prompt_template = CHIEF_STRATEGIST_ADVICE_PROMPT_PERSIAN
    else:
        prompt_template = CHIEF_STRATEGIST_ADVICE_PROMPT
        
    advice_prompt = prompt_template.format(
        client_profile=client_profile,
        market_analysis_summary=market_analysis_summary,
        key_market_data=key_market_data,
        knowledge_base_strategies=knowledge_base_strategies,
        format_instructions=parser.get_format_instructions()
    )
    print(f"---Strategic Advisor: Generated advice prompt (first 500 chars): {advice_prompt[:500]}---")

    advice_response = await llm.ainvoke([HumanMessage(content=advice_prompt)])
    print(f"---Strategic Advisor: LLM advice response received. Content (first 500 chars): {advice_response.content[:500]}---")
    
    try:
        strategic_advice = parser.parse(advice_response.content)
        print(f"---Strategic Advisor: Successfully parsed strategic advice.---")
    except Exception as e:
        print(f"---Strategic Advisor: Failed to parse JSON from advice response. Error: {e}---")
        print(f"---Strategic Advisor: Unparsable content: {advice_response.content}---")
        strategic_advice = {"error": "Failed to generate valid JSON advice.", "exception": str(e)}

    print("---Strategic Advisor Finished---")
    return strategic_advice

if __name__ == '__main__':
    async def main():
        # Mock data for testing - the agent will now run its own research
        mock_work_order = {
            "client_type": "investor",
            "primary_task": "investment_strategy",
            "key_information": {
                "location": "Tehran, Iran",
                "budget": "500,000",
                "property_type": "apartment"
            }
        }
        
        # To test with a specific date:
        advice = await run_strategic_advisor(mock_work_order, report_date="21 - 3 - 2015, 21 - 3 -2014")

        # To test with the default (current) date:
        #advice = await run_strategic_advisor(mock_work_order)
        
        # The output is a dict, so we can dump it directly
        print("\n\n--- Strategic Advisor Test Results ---")
        print(json.dumps(advice, indent=2))
        #save the result to a file
        with open("strategic_advisor_result.json", "w") as f:
            json.dump(advice, f, indent=2)

    asyncio.run(main())