"""
Work Order Form - Standard structure for processing client requests
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ClientType(Enum):
    """Types of clients the real estate firm serves"""
    INVESTOR = "investor"
    HOMEBUYER = "homebuyer" 
    POLICYMAKER = "policymaker"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"

class TaskType(Enum):
    """Types of tasks the firm can handle"""
    COMPARE_REGIONS = "compare_regions"
    VALUATE_PROPERTY = "valuate_property"
    MARKET_ANALYSIS = "market_analysis"
    INVESTMENT_STRATEGY = "investment_strategy"
    PRICE_PREDICTION = "price_prediction"
    RENT_ANALYSIS = "rent_analysis"
    POLICY_IMPACT = "policy_impact"
    SCENARIO_ANALYSIS = "scenario_analysis"

class PropertySpecs(BaseModel):
    """Property specifications extracted from user query"""
    location: Optional[str] = Field(None, description="Property location or area")
    property_type: Optional[str] = Field(None, description="Type of property (apartment, house, commercial, etc.)")
    size: Optional[str] = Field(None, description="Property size or area")
    price_range: Optional[str] = Field(None, description="Budget or price range mentioned")
    special_features: List[str] = Field(default_factory=list, description="Any special features mentioned")

class WorkOrder(BaseModel):
    """
    Standard Work Order Form that the Receptionist creates from user queries
    """
    # Basic identification
    order_id: str = Field(description="Unique identifier for this work order")
    created_at: datetime = Field(default_factory=datetime.now, description="When this order was created")
    
    # Client information
    client_type: ClientType = Field(description="Type of client making the request")
    client_persona: str = Field(description="Detailed persona description of the client")
    
    # Task specification
    primary_task: TaskType = Field(description="Primary task type requested")
    secondary_tasks: List[TaskType] = Field(default_factory=list, description="Additional related tasks")
    
    # Original query
    raw_query: str = Field(description="Original user query as received")
    processed_query: str = Field(description="Cleaned and processed version of the query")
    
    # Extracted information
    key_information: Dict[str, Any] = Field(default_factory=dict, description="Key facts extracted from query")
    property_specs: Optional[PropertySpecs] = Field(None, description="Property specifications if applicable")
    
    # Requirements and constraints
    urgency_level: str = Field(default="normal", description="Urgency level: low, normal, high, urgent")
    required_agents: List[str] = Field(default_factory=list, description="List of specialist agents needed")
    deliverables: List[str] = Field(default_factory=list, description="Expected outputs/deliverables")
    
    # Processing metadata
    status: str = Field(default="pending", description="Current status of the work order")
    assigned_agents: Dict[str, str] = Field(default_factory=dict, description="Agents assigned to tasks")
    
    def add_agent_requirement(self, agent_name: str, reason: str):
        """Add an agent to the required agents list with reasoning"""
        if agent_name not in self.required_agents:
            self.required_agents.append(agent_name)
            self.key_information[f"{agent_name}_requirement"] = reason
    
    def update_status(self, new_status: str):
        """Update the work order status"""
        self.status = new_status
    
    def assign_agent(self, task: str, agent_id: str):
        """Assign an agent to a specific task"""
        self.assigned_agents[task] = agent_id
    
    def to_summary(self) -> str:
        """Generate a human-readable summary of the work order"""
        return f"""
Work Order #{self.order_id}
Client: {self.client_type.value} ({self.client_persona})
Task: {self.primary_task.value}
Query: {self.processed_query}
Required Agents: {', '.join(self.required_agents)}
Status: {self.status}
        """.strip() 