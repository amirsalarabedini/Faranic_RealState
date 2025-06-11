"""
Query Understanding Agent - User Intent Analysis and Work Order Creation
"""

import sys
import os
from typing import Dict, Any
import json
import uuid
from datetime import datetime



from src.agents.core.base_agent import BaseAgent
from src.agents.core.work_order import WorkOrder, ClientType, TaskType, PropertySpecs
from src.agents.core.agent_communication import AgentMessage
from src.agents.prompts import QUERY_UNDERSTANDING_PROMPT
from langchain_core.messages import HumanMessage

class QueryUnderstandingAgent(BaseAgent):
    """
    The QueryUnderstandingAgent analyzes user queries and creates standardized Work Orders.
    
    This agent is responsible for:
    1. Understanding who the client is (investor, homebuyer, policymaker, etc.)
    2. Identifying what they want (compare regions, valuate property, etc.)
    3. Extracting key information from their query
    4. Creating a structured Work Order Form
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id, "QueryUnderstandingAgent")
        self.analysis_prompt = QUERY_UNDERSTANDING_PROMPT
    
    async def analyze_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query and extract structured information
        """
        try:
            # Use LLM to analyze the query
            response = await self.llm.ainvoke([
                HumanMessage(content=self.analysis_prompt.format(user_query=user_query))
            ])
            
            # Log the raw response for debugging
            self.log_activity("Raw LLM response", {"response": response.content[:200]})
            
            # Extract JSON from markdown code blocks if present
            content = response.content.strip()
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()  # Remove ```json and ```
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()  # Remove ``` and ```
            
            # Parse the JSON response
            analysis = json.loads(content)
            
            # Validate and clean the analysis
            analysis = self._validate_analysis(analysis)
            
            return analysis
            
        except json.JSONDecodeError as e:
            self.log_activity("JSON parsing error in query analysis", {
                "error": str(e), 
                "response_content": response.content,
                "response_type": type(response.content).__name__,
                "response_length": len(response.content) if response.content else 0
            })
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            self.log_activity("Error in query analysis", {"error": str(e)})
            raise e
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the analysis results"""
        
        # Validate client_type
        valid_client_types = [ct.value for ct in ClientType]
        client_type = analysis.get("client_type")
        if not client_type or client_type not in valid_client_types:
            raise ValueError(f"Invalid or missing 'client_type'. Found '{client_type}', expected one of {valid_client_types}")

        # Validate primary_task
        valid_task_types = [tt.value for tt in TaskType]
        primary_task = analysis.get("primary_task")
        if not primary_task or primary_task not in valid_task_types:
            raise ValueError(f"Invalid or missing 'primary_task'. Found '{primary_task}', expected one of {valid_task_types}")

        # Ensure required fields exist. Fallback logic has been removed.
        required_fields = [
            "client_persona",
            "secondary_tasks",
            "processed_query",
            "key_information",
            "property_specs",
            "urgency_level",
            "required_agents",
            "deliverables",
        ]
        missing_fields = [field for field in required_fields if field not in analysis]
        if missing_fields:
            raise ValueError(f"Missing required fields in analysis: {', '.join(missing_fields)}")

        return analysis
    
    def create_work_order(self, analysis: Dict[str, Any], original_query: str) -> WorkOrder:
        """
        Create a standardized Work Order from the analysis results
        """
        try:
            # Create property specs if they exist
            property_specs = None
            if analysis.get("property_specs") and any(analysis["property_specs"].values()):
                # Convert any numeric values to strings for PropertySpecs
                specs_data = analysis["property_specs"].copy()
                for key, value in specs_data.items():
                    if value is not None and not isinstance(value, (str, list)):
                        specs_data[key] = str(value)
                
                property_specs = PropertySpecs(**specs_data)
            
            # Create the work order
            work_order = WorkOrder(
                order_id=str(uuid.uuid4()),
                client_type=ClientType(analysis["client_type"]),
                client_persona=analysis["client_persona"],
                primary_task=TaskType(analysis["primary_task"]),
                secondary_tasks=[TaskType(task) for task in analysis.get("secondary_tasks", []) if task in [t.value for t in TaskType]],
                raw_query=original_query,
                processed_query=analysis["processed_query"],
                key_information=analysis["key_information"],
                property_specs=property_specs,
                urgency_level=analysis["urgency_level"],
                required_agents=analysis["required_agents"],
                deliverables=analysis["deliverables"]
            )
            
            self.log_activity("Work order created successfully", {
                "order_id": work_order.order_id,
                "client_type": work_order.client_type.value,
                "primary_task": work_order.primary_task.value
            })
            
            return work_order
            
        except Exception as e:
            self.log_activity("Error creating work order", {"error": str(e)})
            raise e
    
    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
        """
        Process a user query work request and return a completed Work Order
        """
        try:
            # Extract the user query from the request
            user_query = request_message.content.get("user_query", "")
            if not user_query:
                raise ValueError("No user query provided in work request")
            
            self.log_activity("Processing user query", {"query_preview": user_query[:100]})
            
            # Analyze the user query
            analysis = await self.analyze_user_query(user_query)
            
            # Create work order from analysis
            completed_work_order = self.create_work_order(analysis, user_query)
            
            # Prepare the response
            result = {
                "agent_type": self.agent_type,
                "task_completed": "user_intent_analysis",
                "work_order": completed_work_order.dict(),
                "analysis_summary": {
                    "client_identified": analysis["client_type"],
                    "task_identified": analysis["primary_task"],
                    "agents_required": analysis["required_agents"],
                    "urgency": analysis["urgency_level"]
                },
                "recommendations": self._generate_recommendations(completed_work_order),
                "completed_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.log_activity("Error processing work request", {"error": str(e)})
            raise e
    
    def _generate_recommendations(self, work_order: WorkOrder) -> Dict[str, Any]:
        """Generate recommendations for handling this work order"""
        recommendations = {
            "workflow_suggestions": [],
            "priority_adjustments": {},
            "additional_considerations": []
        }
        
        # Workflow suggestions based on task type
        if work_order.primary_task == TaskType.VALUATE_PROPERTY:
            recommendations["workflow_suggestions"] = [
                "Start with Field Researcher for comparable sales data",
                "Then use Appraiser for detailed valuation",
                "Consider Strategic Advisor for market context"
            ]
        elif work_order.primary_task == TaskType.INVESTMENT_STRATEGY:
            recommendations["workflow_suggestions"] = [
                "Begin with Strategic Advisor for investment principles",
                "Use Field Researcher for current market data",
                "Consider Futurist for scenario analysis"
            ]
        elif work_order.primary_task == TaskType.MARKET_ANALYSIS:
            recommendations["workflow_suggestions"] = [
                "Start with Field Researcher for current data",
                "Use Strategic Advisor for market interpretation",
                "Consider Futurist for trends and forecasts"
            ]
        
        # Priority adjustments based on client type
        if work_order.client_type == ClientType.POLICYMAKER:
            recommendations["priority_adjustments"]["increase_research_depth"] = True
            recommendations["additional_considerations"].append("Ensure policy-relevant data inclusion")
        
        return recommendations
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the QueryUnderstandingAgent"""
        return {
            "agent_type": "QueryUnderstandingAgent",
            "primary_function": "User Intent Analysis",
            "capabilities": [
                "Analyze user queries and extract intent",
                "Identify client types and personas",
                "Classify task types and requirements",
                "Create standardized Work Orders",
                "Recommend specialist agent assignments",
                "Assess urgency and priority levels"
            ],
            "input_types": ["natural_language_queries"],
            "output_types": ["work_orders", "client_analysis", "workflow_recommendations"],
            "languages_supported": ["English", "Persian"],
            "specializations": [
                "Real estate client classification",
                "Task type identification", 
                "Information extraction",
                "Workflow planning"
            ]
        } 