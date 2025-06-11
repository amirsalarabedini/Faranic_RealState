"""
LangGraph-based Multi-Agent Communication System
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from enum import Enum

class MessageType(Enum):
    """Types of messages in the multi-agent system"""
    WORK_REQUEST = "work_request"
    STATUS_UPDATE = "status_update"
    REPORT_SUBMISSION = "report_submission"
    TASK_DELEGATION = "task_delegation"
    AGENT_COLLABORATION = "agent_collaboration"
    SYSTEM_NOTIFICATION = "system_notification"
    ERROR_REPORT = "error_report"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MultiAgentState(TypedDict):
    """State schema for multi-agent workflows"""
    messages: Annotated[List[BaseMessage], add_messages]
    active_agents: Dict[str, str]  # agent_id -> agent_type
    workflow_context: Dict[str, Any]
    task_assignments: Dict[str, str]  # task_id -> agent_id
    results_collection: Dict[str, Any]
    error_log: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class AgentMessage(BaseModel):
    """Enhanced message format for LangGraph multi-agent communication"""
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Routing and workflow
    sender_agent: str = Field(description="ID of the sending agent")
    recipient_agents: List[str] = Field(description="IDs of recipient agents")
    message_type: MessageType = Field(description="Type of message")
    workflow_id: Optional[str] = Field(None, description="Associated workflow ID")
    thread_id: Optional[str] = Field(None, description="Thread ID for checkpointing")
    
    # Content
    subject: str = Field(description="Brief subject/title of the message")
    content: Dict[str, Any] = Field(description="Main message content")
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Processing metadata
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    requires_response: bool = Field(default=False)
    correlation_id: Optional[str] = Field(None, description="ID linking related messages")
    parent_message_id: Optional[str] = Field(None, description="Parent message for threading")
    
    # LangGraph integration
    state_snapshot: Optional[Dict[str, Any]] = Field(None, description="State snapshot at message creation")
    
    def to_langchain_message(self) -> BaseMessage:
        """Convert to LangChain message format"""
        additional_kwargs = {
            "message_id": self.message_id,
            "sender_agent": self.sender_agent,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "attachments": self.attachments,
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id
        }
        
        if self.sender_agent == "system":
            return SystemMessage(content=self.subject, additional_kwargs=additional_kwargs)
        elif self.sender_agent == "human":
            return HumanMessage(content=self.subject, additional_kwargs=additional_kwargs)
        else:
            return AIMessage(content=self.subject, additional_kwargs=additional_kwargs)

class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows using LangGraph"""
    
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.active_workflows: Dict[str, StateGraph] = {}
        self.agent_registry: Dict[str, Any] = {}  # agent_id -> agent_instance
        self.message_history: List[AgentMessage] = []
        
    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent in the orchestration system"""
        self.agent_registry[agent_id] = agent_instance
        
    def create_multi_agent_workflow(self, workflow_id: str, participating_agents: List[str]) -> StateGraph:
        """Create a multi-agent workflow graph"""
        workflow = StateGraph(MultiAgentState)
        
        # Add orchestration nodes
        workflow.add_node("initialize_workflow", self._initialize_workflow_node)
        workflow.add_node("route_tasks", self._route_tasks_node)
        workflow.add_node("coordinate_agents", self._coordinate_agents_node)
        workflow.add_node("collect_results", self._collect_results_node)
        workflow.add_node("finalize_workflow", self._finalize_workflow_node)
        workflow.add_node("handle_workflow_error", self._handle_workflow_error_node)
        
        # Add agent-specific nodes
        for agent_id in participating_agents:
            workflow.add_node(f"agent_{agent_id}", self._create_agent_node(agent_id))
        
        # Define workflow edges
        workflow.add_edge(START, "initialize_workflow")
        workflow.add_edge("initialize_workflow", "route_tasks")
        workflow.add_conditional_edges(
            "route_tasks",
            self._route_tasks_decision,
            {
                "coordinate": "coordinate_agents",
                "error": "handle_workflow_error"
            }
        )
        workflow.add_edge("coordinate_agents", "collect_results")
        workflow.add_conditional_edges(
            "collect_results",
            self._collection_decision,
            {
                "complete": "finalize_workflow",
                "continue": "coordinate_agents",
                "error": "handle_workflow_error"
            }
        )
        workflow.add_edge("finalize_workflow", END)
        workflow.add_edge("handle_workflow_error", END)
        
        # Add agent coordination edges
        for agent_id in participating_agents:
            workflow.add_edge(f"agent_{agent_id}", "collect_results")
        
        compiled_workflow = workflow.compile(checkpointer=self.checkpointer)
        self.active_workflows[workflow_id] = compiled_workflow
        
        return compiled_workflow
    
    async def _initialize_workflow_node(self, state: MultiAgentState) -> MultiAgentState:
        """Initialize multi-agent workflow"""
        state["metadata"]["workflow_start"] = datetime.now().isoformat()
        state["metadata"]["status"] = "initializing"
        
        # Initialize message log
        init_message = SystemMessage(
            content="Multi-agent workflow initialized",
            additional_kwargs={"workflow_id": state["metadata"].get("workflow_id")}
        )
        state["messages"].append(init_message)
        
        return state
    
    async def _route_tasks_node(self, state: MultiAgentState) -> MultiAgentState:
        """Route tasks to appropriate agents"""
        try:
            workflow_context = state["workflow_context"]
            task_requirements = workflow_context.get("task_requirements", [])
            
            # Route tasks based on agent capabilities
            for task in task_requirements:
                best_agent = self._find_best_agent_for_task(task, state["active_agents"])
                if best_agent:
                    state["task_assignments"][task["task_id"]] = best_agent
                else:
                    state["error_log"].append({
                        "error": f"No suitable agent found for task {task['task_id']}",
                        "timestamp": datetime.now().isoformat()
                    })
            
            return state
            
        except Exception as e:
            state["error_log"].append({
                "error": f"Task routing error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            return state
    
    async def _coordinate_agents_node(self, state: MultiAgentState) -> MultiAgentState:
        """Coordinate agent execution"""
        # Send work requests to assigned agents
        for task_id, agent_id in state["task_assignments"].items():
            if agent_id in self.agent_registry:
                # Create coordination message
                coord_message = AIMessage(
                    content=f"Task assignment: {task_id}",
                    additional_kwargs={
                        "task_id": task_id,
                        "agent_id": agent_id,
                        "coordination_type": "task_assignment"
                    }
                )
                state["messages"].append(coord_message)
        
        return state
    
    async def _collect_results_node(self, state: MultiAgentState) -> MultiAgentState:
        """Collect results from agents"""
        # Check for completed tasks
        completed_tasks = []
        for task_id, agent_id in state["task_assignments"].items():
            # In a real implementation, this would check agent status
            # For now, we simulate result collection
            if task_id not in state["results_collection"]:
                state["results_collection"][task_id] = {
                    "agent_id": agent_id,
                    "status": "in_progress",
                    "timestamp": datetime.now().isoformat()
                }
        
        return state
    
    async def _finalize_workflow_node(self, state: MultiAgentState) -> MultiAgentState:
        """Finalize the multi-agent workflow"""
        state["metadata"]["workflow_end"] = datetime.now().isoformat()
        state["metadata"]["status"] = "completed"
        
        # Create final summary message
        summary_message = SystemMessage(
            content="Multi-agent workflow completed",
            additional_kwargs={
                "total_tasks": len(state["task_assignments"]),
                "completed_tasks": len(state["results_collection"]),
                "participating_agents": list(state["active_agents"].keys())
            }
        )
        state["messages"].append(summary_message)
        
        return state
    
    async def _handle_workflow_error_node(self, state: MultiAgentState) -> MultiAgentState:
        """Handle workflow errors"""
        state["metadata"]["status"] = "error"
        
        error_summary = {
            "total_errors": len(state["error_log"]),
            "errors": state["error_log"]
        }
        
        error_message = SystemMessage(
            content="Workflow encountered errors",
            additional_kwargs=error_summary
        )
        state["messages"].append(error_message)
        
        return state
    
    def _create_agent_node(self, agent_id: str):
        """Create a node function for a specific agent"""
        async def agent_node(state: MultiAgentState) -> MultiAgentState:
            # Execute agent-specific logic
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                # This would call the agent's LangGraph workflow
                # For now, we simulate agent execution
                
                result_message = AIMessage(
                    content=f"Agent {agent_id} completed processing",
                    additional_kwargs={
                        "agent_id": agent_id,
                        "execution_status": "completed"
                    }
                )
                state["messages"].append(result_message)
            
            return state
        
        return agent_node
    
    def _route_tasks_decision(self, state: MultiAgentState) -> str:
        """Decision function for task routing"""
        if state["error_log"]:
            return "error"
        return "coordinate"
    
    def _collection_decision(self, state: MultiAgentState) -> str:
        """Decision function for result collection"""
        if state["error_log"]:
            return "error"
        
        # Check if all tasks are completed
        all_completed = len(state["results_collection"]) == len(state["task_assignments"])
        return "complete" if all_completed else "continue"
    
    def _find_best_agent_for_task(self, task: Dict[str, Any], active_agents: Dict[str, str]) -> Optional[str]:
        """Find the best agent for a given task"""
        # This would implement agent capability matching
        # For now, return the first available agent
        return list(active_agents.keys())[0] if active_agents else None
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message through the orchestration system"""
        # Add to message history
        self.message_history.append(message)
        
        # Route to appropriate workflow if specified
        if message.workflow_id and message.workflow_id in self.active_workflows:
            workflow = self.active_workflows[message.workflow_id]
            
            # Update workflow state with new message
            config = {"configurable": {"thread_id": message.thread_id or message.workflow_id}}
            
            try:
                current_state = workflow.get_state(config)
                if current_state:
                    # Add message to workflow state
                    langchain_message = message.to_langchain_message()
                    current_state.values["messages"].append(langchain_message)
                    
                return True
            except Exception as e:
                print(f"Error updating workflow state: {e}")
                return False
        
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            config = {"configurable": {"thread_id": workflow_id}}
            
            try:
                state = workflow.get_state(config)
                return {
                    "workflow_id": workflow_id,
                    "status": state.values.get("metadata", {}).get("status", "unknown"),
                    "active_agents": state.values.get("active_agents", {}),
                    "task_assignments": state.values.get("task_assignments", {}),
                    "results_count": len(state.values.get("results_collection", {})),
                    "error_count": len(state.values.get("error_log", []))
                }
            except Exception as e:
                return {"workflow_id": workflow_id, "error": str(e)}
        
        return None
    
    async def execute_workflow(self, workflow_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a multi-agent workflow"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        config = {"configurable": {"thread_id": workflow_id}}
        
        # Execute the workflow
        final_state = await workflow.ainvoke(initial_state, config=config)
        
        return final_state
    
    async def stream_workflow(self, workflow_id: str, initial_state: Dict[str, Any]):
        """Stream workflow execution for real-time updates"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        config = {"configurable": {"thread_id": workflow_id}}
        
        # Stream execution
        async for chunk in workflow.astream(initial_state, config=config):
            yield chunk

# Factory functions for creating standard messages
class MessageFactory:
    """Factory for creating standard message types"""
    
    @staticmethod
    def create_work_request(sender: str, recipients: List[str], task: str, 
                          work_order_data: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> AgentMessage:
        """Create a work request message"""
        return AgentMessage(
            sender_agent=sender,
            recipient_agents=recipients,
            message_type=MessageType.WORK_REQUEST,
            subject=f"Work Request: {task}",
            content={
                "task": task,
                "work_order": work_order_data,
                "instructions": f"Please complete the {task} task as specified."
            },
            priority=priority,
            requires_response=True
        )
    
    @staticmethod
    def create_status_update(sender: str, recipients: List[str], status: str, 
                           details: str, correlation_id: str) -> AgentMessage:
        """Create a status update message"""
        return AgentMessage(
            sender_agent=sender,
            recipient_agents=recipients,
            message_type=MessageType.STATUS_UPDATE,
            subject=f"Status Update: {status}",
            content={
                "status": status,
                "details": details,
                "updated_at": datetime.now().isoformat()
            },
            correlation_id=correlation_id,
            requires_response=False
        )
    
    @staticmethod
    def create_report_submission(sender: str, recipients: List[str], 
                               report_data: Dict[str, Any], correlation_id: str) -> AgentMessage:
        """Create a report submission message"""
        return AgentMessage(
            sender_agent=sender,
            recipient_agents=recipients,
            message_type=MessageType.REPORT_SUBMISSION,
            subject=f"Report from {sender}",
            content={
                "report": report_data,
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            },
            correlation_id=correlation_id,
            requires_response=False
        ) 