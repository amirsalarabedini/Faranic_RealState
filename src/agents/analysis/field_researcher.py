"""
Field Researcher Agent - Web Data Expert for Real Estate Information, now using LangGraph.
"""

import sys
import os

# Add the project root to the Python path to enable direct script execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
import re

# Import the autonomous deep research agent and its configuration
from src.agents.utils.web_deep_research.web_graph import get_deep_research_agent
from src.agents.utils.web_deep_research.configuration import Configuration as WebResearchConfig
from src.agents.utils.web_deep_research.utils import get_today_str
from src.agents.prompts import FIELD_RESEARCHER_EXTRACTION_PROMPT, FIELD_RESEARCHER_TREND_SUMMARY_PROMPT
from src.configs.llm_config import get_default_llm
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from src.agents.analysis.models.field_researcher_models import RealEstateAnalysis


"""
The Field Researcher Agent performs deep, autonomous web research on a given topic
by leveraging the web_graph agent, built on the LangGraph framework.
"""

def format_date_range(date_str: Optional[str]) -> Optional[str]:
    """Formats a date or date range string into MM/DD/YYYY-MM/DD/YYYY format."""
    if not date_str:
        return None
    
    # Normalize separators
    date_str = re.sub(r'[,;/\s]+', '-', date_str)
    parts = date_str.split('-')
    
    # Clean up parts to be just numbers
    cleaned_parts = []
    for part in parts:
        cleaned_parts.extend(re.findall(r'\d+', part))

    if len(cleaned_parts) == 6: # Range like D-M-Y-D-M-Y
        try:
            start_day, start_month, start_year, end_day, end_month, end_year = map(int, cleaned_parts)
            start_date = datetime(start_year, start_month, start_day)
            end_date = datetime(end_year, end_month, end_day)
            return f"{start_date.strftime('%m/%d/%Y')}-{end_date.strftime('%m/%d/%Y')}"
        except ValueError:
            return date_str # Return original if parsing fails
    elif len(cleaned_parts) == 3: # Single date D-M-Y
        try:
            day, month, year = map(int, cleaned_parts)
            date = datetime(year, month, day)
            # For a single date, we might search for that whole day or a range around it.
            # For simplicity, let's just format it and let the API decide.
            # Or, we can create a range for the whole year.
            return f"01/01/{year}-12/31/{year}"
        except ValueError:
            return date_str
            
    return date_str # Return original string if format is not recognized

async def run_field_researcher(topic: str, report_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Runs the field research process.
    
    Args:
        topic: The topic to research.
        report_date: The date or date range to use for the research.
        
    Returns:
        A dictionary containing the research findings.
    """
    print(f"---Running Field Researcher for topic: {topic}---")
    
    time_range_for_search = format_date_range(report_date)
    
    # 1. Get the deep research agent and its configuration
    deep_research_agent = get_deep_research_agent()
    config = WebResearchConfig(time_range=time_range_for_search)

    # 2. Run the deep research to get a report
    graph_result = await deep_research_agent.ainvoke(
        {"topic": topic, "report_date": report_date or get_today_str()},
        config={"configurable": config}
    )
    
    report_content = graph_result.get("final_report")
    
    if not report_content:
        print("---Field Researcher: Deep research did not produce a report.---")
        return {
            "error": "Failed to generate a research report.",
            "structured_data": {},
            "summary": ""
        }

    print("---Field Researcher: Report generated, now extracting data...---")

    # 3. Use an LLM to extract structured data from the report
    llm = get_default_llm()
    parser = JsonOutputParser(pydantic_object=RealEstateAnalysis)
    
    extraction_prompt = FIELD_RESEARCHER_EXTRACTION_PROMPT.format(
        content=report_content,
        format_instructions=parser.get_format_instructions()
    )
    
    extraction_response = await llm.ainvoke([HumanMessage(content=extraction_prompt)])
    
    try:
        # The response is expected to be a JSON string
        structured_data = parser.parse(extraction_response.content)
    except Exception as e:
        print(f"---Field Researcher: Failed to parse structured data from report. Error: {e}---")
        structured_data = {"error": "Failed to parse JSON from the extraction step."}

    print("---Field Researcher: Data extracted, now generating summary...---")
    
    # Convert Pydantic model to dict for serialization, handling potential errors
    structured_data_dict = {}
    if hasattr(structured_data, 'model_dump'):
        structured_data_dict = structured_data.model_dump()
    elif isinstance(structured_data, dict):
        structured_data_dict = structured_data

    # 4. Use an LLM to generate a final summary
    summary_prompt = FIELD_RESEARCHER_TREND_SUMMARY_PROMPT.format(numerical_analysis=json.dumps(structured_data_dict, indent=2))
    
    summary_response = await llm.ainvoke([HumanMessage(content=summary_prompt)])
    summary = summary_response.content

    print("---Field Researcher: Process complete.---")
    
    return {
        "structured_data": structured_data_dict,
        "summary": summary,
        "full_report": report_content  # Optionally return the full report
    }


if __name__ == '__main__':
    # This allows for direct testing of the field researcher agent
    async def main():
        topic_to_research = "Real estate investment trends in Tehran"
        
        # To test with a specific date range:
        results = await run_field_researcher(topic_to_research, report_date="21-3-2014 to 21-3-2015")
        
        # To test with the default (current) date:
        # results = await run_field_researcher(topic_to_research)
        
        print("\n\n--- Field Researcher Test Results ---")
        print("Summary:", results.get("summary"))
        print("\nStructured Data:")
        # The returned data is already a dict, so it can be directly dumped to JSON
        print(json.dumps(results.get("structured_data"), indent=2))
        # print("\nFull Report:", results.get("full_report")) # Uncomment to see the full report

    asyncio.run(main())
