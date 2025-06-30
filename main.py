"""
Main Orchestrator for the Faranic Real Estate Multi-Agent System
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import re

from src.agents.specialists.query_understanding_agent import run_query_understanding_agent
from src.agents.specialists.strategic_advisor import run_strategic_advisor
from src.agents.specialists.generate_report_agent import run_generate_report_agent, format_strategic_advice

# Ensure all necessary paths are set up
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def format_work_order(work_order: Dict[str, Any], language: str = "English") -> str:
    """Formats the work order dictionary into a readable markdown string."""
    
    if language == "Persian":
        labels = {
            "client_type": "نوع مشتری", "client_persona": "پرسونای مشتری",
            "primary_task": "وظیفه اصلی", "processed_query": "درخواست پردازش‌شده",
            "key_information": "اطلاعات کلیدی", "property_specs": "مشخصات ملک",
            "urgency_level": "سطح فوریت", "location": "مکان", "budget": "بودجه",
            "timeline": "بازه زمانی", "property_type": "نوع ملک",
            "specific_requirements": "نیازمندی‌های خاص", "size_sqft": "متراژ",
            "price_range": "محدوده قیمت", "number_of_bedrooms": "تعداد اتاق خواب",
            "number_of_bathrooms": "تعداد حمام", "amenities": "امکانات رفاهی",
            "year_built": "سال ساخت", "property_condition": "وضعیت ملک",
            "special_features": "ویژگی های خاص",
        }
        title = "#### ✅ سفارش کار ایجاد شد"
        summary_text = "مشاهده JSON خام"
    else:
        labels = {
            "client_type": "Client Type", "client_persona": "Client Persona",
            "primary_task": "Primary Task", "processed_query": "Processed Query",
            "key_information": "Key Information", "property_specs": "Property Specifications",
            "urgency_level": "Urgency Level", "location": "Location", "budget": "Budget",
            "timeline": "Timeline", "property_type": "Property Type",
            "specific_requirements": "Specific Requirements", "size_sqft": "Size (sqft)",
            "price_range": "Price Range", "number_of_bedrooms": "Bedrooms",
            "number_of_bathrooms": "Bathrooms", "amenities": "Amenities",
            "year_built": "Year Built", "property_condition": "Property Condition",
            "special_features": "Special Features",
        }
        title = "#### ✅ Work Order Created"
        summary_text = "View Raw JSON"

    md_lines = [title]
    
    top_level_keys = ["client_type", "primary_task", "urgency_level", "client_persona", "processed_query"]
    for key in top_level_keys:
        value = work_order.get(key)
        if value:
            label = labels.get(key, key.replace('_', ' ').title())
            md_lines.append(f"- **{label}**: {value}")

    nested_keys = ["key_information", "property_specs"]
    for nested_key in nested_keys:
        nested_dict = work_order.get(nested_key)
        if nested_dict and any(nested_dict.values()):
            label = labels.get(nested_key, nested_key.replace('_', ' ').title())
            md_lines.append(f"- **{label}**:")
            for key, value in nested_dict.items():
                if value:
                    item_label = labels.get(key, key.replace('_', ' ').title())
                    value_str = ", ".join(map(str, value)) if isinstance(value, list) else str(value)
                    md_lines.append(f"  - **{item_label}**: {value_str}")
    
    return "\n".join(md_lines)

def is_persian(text: str) -> bool:
    """Checks if the text contains Persian characters."""
    return bool(re.search('[\u0600-\u06FF]', text))

async def main(user_query: str, report_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """
    Main function to orchestrate the multi-agent workflow, yielding results as they are generated.
    """
    yield "### Starting Faranic Real Estate Agent Workflow...\n"
    
    # 0. Detect Language
    language = "Persian" if is_persian(user_query) else "English"
    yield f"\n**Orchestrator:** Language detected: {language}\n"

    # 1. Understand the user's query and create a work order
    yield f"\n**Orchestrator:** Understanding user query: '{user_query}'\n"
    work_order = run_query_understanding_agent(user_query, language)
    work_order_md = format_work_order(work_order, language)
    yield work_order_md

    # 2. Define the report date
    if report_date is None:
        report_date = datetime.now().strftime("%B %d, %Y")
        yield f"\n**Orchestrator:** Using current date: {report_date}\n"
    
    # 3. Run the Strategic Advisor to get comprehensive advice
    yield "\n---\n### Running Strategic Advisor...\n"
    strategic_advice = await run_strategic_advisor(work_order, report_date, language)

    if "error" in strategic_advice:
        error_md = f"**Orchestrator:** Halting workflow due to error from Strategic Advisor: {strategic_advice['error']}"
        yield error_md
        return

    formatted_advice_for_stream = format_strategic_advice(strategic_advice)
    advice_md = f"#### ✅ Strategic Advice Received\n{formatted_advice_for_stream}"
    yield advice_md

    # 4. Run the Generate Report Agent to create the final output
    yield "\n---\n### Generating Final Report...\n"
    final_report = await run_generate_report_agent(work_order, strategic_advice, language)
    
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