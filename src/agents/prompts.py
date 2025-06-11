"""
Centralized prompts for all agents in the Faranic Real Estate multi-agent system.
"""

from langchain_core.prompts import PromptTemplate

# Receptionist Agent Prompts
QUERY_UNDERSTANDING_PROMPT = PromptTemplate(
    input_variables=["user_query"],
    template="""
You are an expert receptionist at a prestigious real estate consulting firm. Your job is to analyze client queries and extract structured information.

IMPORTANT: You must respond with ONLY valid JSON. Do not include any text before or after the JSON object.

USER QUERY: {user_query}

Analyze this query and respond with this exact JSON structure (replace values as appropriate):

{{
    "client_type": "one of: investor, homebuyer, policymaker, developer, researcher",
    "client_persona": "detailed description of the client based on their query and language",
    "primary_task": "one of: compare_regions, valuate_property, market_analysis, investment_strategy, price_prediction, rent_analysis, policy_impact, scenario_analysis, investment_recommendation, risk_assessment, market_insights, investment_prospects",
    "secondary_tasks": [],
    "processed_query": "cleaned and clarified version of the user's query",
    "key_information": {{
        "budget": null,
        "location": null, 
        "timeline": null,
        "property_type": null,
        "specific_requirements": []
    }},
    "property_specs": {{
        "location": null,
        "property_type": null,
        "size": null, 
        "price_range": null,
        "special_features": []
    }},
    "urgency_level": "normal",
    "required_agents": ["field_researcher", "strategic_advisor"],
    "deliverables": ["analysis_report"]
}}

Guidelines:
- Respond with ONLY the JSON object
- Use null for missing information, not empty strings
- Use valid enum values for client_type and primary_task
- Required agents can be: field_researcher, strategic_advisor, appraiser, futurist, writer_editor
- Infer client type from context and language used
- Extract property specifications if mentioned
    """.strip()
)

# Field Researcher Agent Prompts
FIELD_RESEARCHER_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["content"],
    template="""
You are a real estate data analyst. Extract all numerical data, statistics, and factual information from the following content.

Content to analyze:
{content}

Please provide a JSON response with the following structure:
{{
    "prices": {{
        "average_price_per_sqm": "extracted price if available",
        "price_range": "price range if available",
        "price_trend": "increasing/decreasing/stable if mentioned"
    }},
    "rental_data": {{
        "average_rent": "rental price if available",
        "rental_yield": "rental yield percentage if available",
        "rental_trend": "trend information if available"
    }},
    "market_indicators": {{
        "transaction_volume": "number of transactions if available",
        "market_growth": "growth percentage if available",
        "supply_demand": "supply/demand information if available"
    }},
    "economic_factors": {{
        "inflation_rate": "inflation data if available",
        "interest_rates": "interest rate data if available",
        "economic_indicators": ["list of other economic factors mentioned"]
    }},
    "geographical_data": {{
        "location": "specific location mentioned",
        "district_data": ["district-specific information if available"]
    }},
    "time_period": "time period the data refers to",
    "data_quality": "assessment of data reliability and recency",
    "key_statistics": ["list of the most important numerical findings"]
}}

Focus on extracting actual numbers, percentages, and quantifiable data. If no data is available for a category, use null.
""".strip()
)

FIELD_RESEARCHER_TREND_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["numerical_analysis"],
    template="""
Based on the following numerical real estate data analysis, create a concise trend summary:

Data: {numerical_analysis}

Provide a brief summary (2-3 sentences) highlighting:
1. Key price trends
2. Market direction (growing/declining/stable)
3. Most important findings

Summary:
""".strip()
)

# Strategy Extraction Agent Prompts
STRATEGY_EXTRACTION_FACTS_PROMPT = PromptTemplate(
    input_variables=["client_type", "task"],
    template="""
Extract key facts and market principles for a {client_type} client considering {task}.

Location: {location}
""".strip()
)

STRATEGY_EXTRACTION_METHODS_PROMPT = PromptTemplate(
    input_variables=["client_type", "task", "location"],
    template="""
Identify specific investment methods, step-by-step strategies, and practical actions for a {client_type} client considering {task}.

Location: {location}
""".strip()
) 
