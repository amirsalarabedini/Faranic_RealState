"""
Query Understanding Agent - User Intent Analysis and Work Order Creation
"""

import sys
import os
from typing import Dict, Any
import json
import uuid
from datetime import datetime

from src.agents.prompts import QUERY_UNDERSTANDING_PROMPT, QUERY_UNDERSTANDING_PROMPT_PERSIAN
from langchain_core.messages import HumanMessage
from src.configs.llm_config import get_default_llm

def run_query_understanding_agent(query: str, language: str = "English") -> Dict[str, Any]:
    """
    The QueryUnderstandingAgent analyzes user queries and creates standardized Work Orders.
    
    This agent is responsible for:
    1. Understanding who the client is (investor, homebuyer, policymaker, etc.)
    2. Identifying what they want (compare regions, valuate property, etc.)
    3. Extracting key information from their query
    4. Creating a structured Work Order Form
    """
    llm = get_default_llm()
    
    if language == "Persian":
        prompt_template = QUERY_UNDERSTANDING_PROMPT_PERSIAN
    else:
        prompt_template = QUERY_UNDERSTANDING_PROMPT
        
    prompt = prompt_template.format(user_query=query)
    
    messages = [HumanMessage(content=prompt)]
    
    llm_response = llm.invoke(messages)
    
    # Extract the JSON part from the response
    try:
        # The response might be a string or a message object
        content = llm_response.content if hasattr(llm_response, 'content') else llm_response
        print(f"---LLM Response Content---\n{content}\n--------------------------")
        json_part = content.split("```json")[1].split("```")[0].strip()
        work_order = json.loads(json_part)
    except (IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing LLM response: {e}")
        # Fallback to a default work order
        work_order = {
            "client_type": "unknown",
            "request_type": "unknown",
            "key_info": {"query": query}
        }
        
    # Add metadata to the work order
    work_order['work_order_id'] = str(uuid.uuid4())
    work_order['timestamp'] = datetime.utcnow().isoformat()
    
    return work_order
