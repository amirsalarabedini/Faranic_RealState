"""
LangGraph-enhanced Work Order System - Standard structure for processing client requests
"""

from enum import Enum
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

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
    FIELD_RESEARCH = "field_research"
    TREND_ANALYSIS = "trend_analysis"
    DEEP_DIVE_RESEARCH = "deep_dive_research"
    STRATEGY_EXTRACTION = "strategy_extraction"
    VALUATE_PROPERTY = "valuate_property"
    MARKET_ANALYSIS = "market_analysis"
    INVESTMENT_STRATEGY = "investment_strategy"
    INVESTMENT_PROSPECTS = "investment_prospects"
    PRICE_PREDICTION = "price_prediction"
    RENT_ANALYSIS = "rent_analysis"
    POLICY_IMPACT = "policy_impact"
    SCENARIO_ANALYSIS = "scenario_analysis"
    INVESTMENT_RECOMMENDATION = "investment_recommendation"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_INSIGHTS = "market_insights"

class WorkflowStatus(Enum):
    """Workflow status for LangGraph integration"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    AGENT_ASSIGNED = "agent_assigned"
    PROCESSING = "processing"
    REVIEW = "review"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class PropertySpecs(BaseModel):
    """Property specifications extracted from user query"""
    location: Optional[str] = Field(None, description="Property location or area")
    property_type: Optional[str] = Field(None, description="Type of property (apartment, house, commercial, etc.)")
    size: Optional[str] = Field(None, description="Property size or area")
    price_range: Optional[str] = Field(None, description="Budget or price range mentioned")
    special_features: List[str] = Field(default_factory=list, description="Any special features mentioned")

class TaskRequirement(BaseModel):
    """Individual task requirement within a work order"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = Field(description="Type of task to be performed")
    description: str = Field(description="Detailed description of the task")
    required_agent_type: Optional[str] = Field(None, description="Specific agent type required")
    priority: str = Field(default="normal", description="Task priority level")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs this task depends on")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    
class WorkflowCheckpoint(BaseModel):
    """Checkpoint for workflow state persistence"""
    checkpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    workflow_state: Dict[str, Any] = Field(description="Current workflow state")
    completed_tasks: List[str] = Field(default_factory=list)
    pending_tasks: List[str] = Field(default_factory=list)
    agent_assignments: Dict[str, str] = Field(default_factory=dict)

class WorkOrderState(TypedDict):
    """LangGraph state schema for work order processing"""
    messages: Annotated[List[BaseMessage], add_messages]
    work_order: "WorkOrder"
    current_status: WorkflowStatus
    task_progress: Dict[str, Any]
    agent_assignments: Dict[str, str]
    results: Dict[str, Any]
    error_log: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class WorkOrder(BaseModel):
    """
    Enhanced Work Order Form with LangGraph workflow integration
    """
    # Basic identification
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this work order")
    created_at: datetime = Field(default_factory=datetime.now, description="When this order was created")
    
    # Client information
    client_type: ClientType = Field(description="Type of client making the request")
    client_persona: str = Field(description="Detailed persona description of the client")
    
    # Task specification
    primary_task: TaskType = Field(description="Primary task type requested")
    secondary_tasks: List[TaskType] = Field(default_factory=list, description="Additional related tasks")
    task_requirements: List[TaskRequirement] = Field(default_factory=list, description="Detailed task requirements")
    
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
    
    # LangGraph workflow integration
    workflow_id: Optional[str] = Field(None, description="Associated LangGraph workflow ID")
    thread_id: Optional[str] = Field(None, description="Thread ID for checkpointing")
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING, description="Current workflow status")
    
    # Processing metadata
    assigned_agents: Dict[str, str] = Field(default_factory=dict, description="Agents assigned to tasks")
    workflow_checkpoints: List[WorkflowCheckpoint] = Field(default_factory=list, description="Workflow state checkpoints")
    execution_history: List[Dict[str, Any]] = Field(default_factory=list, description="Execution history")
    
    # Results and outputs
    results: Dict[str, Any] = Field(default_factory=dict, description="Task results")
    final_deliverable: Optional[Dict[str, Any]] = Field(None, description="Final compiled deliverable")
    
    def add_task_requirement(self, task_type: TaskType, description: str, 
                           required_agent_type: Optional[str] = None, 
                           priority: str = "normal") -> str:
        """Add a task requirement to the work order"""
        task_req = TaskRequirement(
            task_type=task_type,
            description=description,
            required_agent_type=required_agent_type,
            priority=priority
        )
        self.task_requirements.append(task_req)
        return task_req.task_id
    
    def add_agent_requirement(self, agent_name: str, reason: str):
        """Add an agent to the required agents list with reasoning"""
        if agent_name not in self.required_agents:
            self.required_agents.append(agent_name)
            self.key_information[f"{agent_name}_requirement"] = reason
    
    def update_status(self, new_status: WorkflowStatus, details: Optional[str] = None):
        """Update the work order status with history tracking"""
        old_status = self.status
        self.status = new_status
        
        # Add to execution history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "status_change",
            "from_status": old_status.value,
            "to_status": new_status.value,
            "details": details
        })
    
    def assign_agent(self, task_id: str, agent_id: str):
        """Assign an agent to a specific task"""
        self.assigned_agents[task_id] = agent_id
        
        # Add to execution history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "agent_assignment",
            "task_id": task_id,
            "agent_id": agent_id
        })
    
    def create_checkpoint(self, workflow_state: Dict[str, Any]) -> str:
        """Create a workflow checkpoint"""
        # Determine completed and pending tasks
        completed_tasks = []
        pending_tasks = []
        
        for task_req in self.task_requirements:
            if task_req.task_id in self.results:
                completed_tasks.append(task_req.task_id)
            else:
                pending_tasks.append(task_req.task_id)
        
        checkpoint = WorkflowCheckpoint(
            workflow_state=workflow_state,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            agent_assignments=self.assigned_agents.copy()
        )
        
        self.workflow_checkpoints.append(checkpoint)
        return checkpoint.checkpoint_id
    
    def get_latest_checkpoint(self) -> Optional[WorkflowCheckpoint]:
        """Get the most recent workflow checkpoint"""
        if self.workflow_checkpoints:
            return self.workflow_checkpoints[-1]
        return None
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore work order state from a specific checkpoint"""
        for checkpoint in self.workflow_checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                self.assigned_agents = checkpoint.agent_assignments.copy()
                # Additional restoration logic would go here
                return True
        return False
    
    def add_result(self, task_id: str, result: Dict[str, Any], agent_id: str):
        """Add a task result"""
        self.results[task_id] = {
            "result": result,
            "completed_by": agent_id,
            "completed_at": datetime.now().isoformat(),
            "task_type": self._get_task_type_by_id(task_id)
        }
        
        # Add to execution history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "task_completed",
            "task_id": task_id,
            "agent_id": agent_id,
            "result_summary": self._summarize_result(result)
        })
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of current progress"""
        total_tasks = len(self.task_requirements)
        completed_tasks = len(self.results)
        
        return {
            "order_id": self.order_id,
            "status": self.status.value,
            "progress": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "assigned_agents": list(self.assigned_agents.values()),
            "estimated_completion": self._estimate_completion_time(),
            "current_bottlenecks": self._identify_bottlenecks()
        }
    
    def to_workflow_state(self) -> WorkOrderState:
        """Convert to LangGraph workflow state"""
        return {
            "messages": [],
            "work_order": self,
            "current_status": self.status,
            "task_progress": self._calculate_task_progress(),
            "agent_assignments": self.assigned_agents.copy(),
            "results": self.results.copy(),
            "error_log": [],
            "metadata": {
                "order_id": self.order_id,
                "created_at": self.created_at.isoformat(),
                "client_type": self.client_type.value,
                "urgency_level": self.urgency_level
            }
        }
    
    def to_summary(self) -> str:
        """Generate a human-readable summary of the work order"""
        progress = self.get_progress_summary()
        
        return f"""
Work Order #{self.order_id}
Status: {self.status.value}
Client: {self.client_type.value} ({self.client_persona})
Primary Task: {self.primary_task.value}
Query: {self.processed_query}
Progress: {progress['progress']['completed_tasks']}/{progress['progress']['total_tasks']} tasks ({progress['progress']['completion_percentage']:.1f}%)
Required Agents: {', '.join(self.required_agents)}
Assigned Agents: {', '.join(set(self.assigned_agents.values()))}
Workflow ID: {self.workflow_id or 'Not assigned'}
        """.strip()
    
    def _get_task_type_by_id(self, task_id: str) -> Optional[str]:
        """Get task type by task ID"""
        for task_req in self.task_requirements:
            if task_req.task_id == task_id:
                return task_req.task_type.value
        return None
    
    def _summarize_result(self, result: Dict[str, Any]) -> str:
        """Create a brief summary of a result"""
        if isinstance(result, dict):
            return f"Result with {len(result)} items"
        return str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
    
    def _calculate_task_progress(self) -> Dict[str, Any]:
        """Calculate detailed task progress"""
        progress = {}
        for task_req in self.task_requirements:
            progress[task_req.task_id] = {
                "task_type": task_req.task_type.value,
                "status": "completed" if task_req.task_id in self.results else "pending",
                "assigned_agent": self.assigned_agents.get(task_req.task_id),
                "priority": task_req.priority
            }
        return progress
    
    def _estimate_completion_time(self) -> Optional[str]:
        """Estimate completion time based on remaining tasks"""
        pending_tasks = [task for task in self.task_requirements if task.task_id not in self.results]
        
        if not pending_tasks:
            return "Completed"
        
        # Simple estimation based on task count and average duration
        total_estimated_minutes = sum(task.estimated_duration or 30 for task in pending_tasks)
        
        if total_estimated_minutes < 60:
            return f"~{total_estimated_minutes} minutes"
        else:
            hours = total_estimated_minutes // 60
            minutes = total_estimated_minutes % 60
            return f"~{hours}h {minutes}m"
    
    def _identify_bottlenecks(self) -> List[str]:
        """Identify potential bottlenecks in the workflow"""
        bottlenecks = []
        
        # Check for unassigned high-priority tasks
        for task_req in self.task_requirements:
            if (task_req.task_id not in self.assigned_agents and 
                task_req.priority in ["high", "urgent"] and 
                task_req.task_id not in self.results):
                bottlenecks.append(f"Unassigned high-priority task: {task_req.task_type.value}")
        
        # Check for dependency issues
        for task_req in self.task_requirements:
            if task_req.dependencies:
                for dep_id in task_req.dependencies:
                    if dep_id not in self.results:
                        bottlenecks.append(f"Task {task_req.task_type.value} waiting for dependency")
                        break
        
        return bottlenecks 