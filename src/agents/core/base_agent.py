"""
LangGraph-based Agent Foundation - Using state machines and workflows
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import uuid
import asyncio
from datetime import datetime

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from src.configs.llm_config import get_default_llm
from .work_order import WorkOrder

class AgentState(TypedDict):
    """State schema for LangGraph agent workflows"""
    messages: Annotated[List[Any], add_messages]
    agent_id: str
    agent_type: str
    status: str
    current_task: Optional[Dict[str, Any]]
    work_order: Optional[WorkOrder]
    results: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """
    LangGraph-based base agent using state machines and workflows.
    Provides durable execution, human-in-the-loop, and comprehensive memory.
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type or self.__class__.__name__
        self.llm = get_default_llm()
        
        # LangGraph components
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)
        
        # Agent capabilities and tools
        self.tools = self._initialize_tools()
        self.capabilities = self.get_capabilities()
        
        # State tracking
        self.status = "idle"
        self.session_history: List[Dict[str, Any]] = []
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for this agent"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("validate_request", self._validate_request_node)
        workflow.add_node("process_work", self._process_work_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add conditional edges
        workflow.add_edge(START, "initialize")
        workflow.add_conditional_edges(
            "initialize",
            self._route_after_init,
            {
                "validate": "validate_request",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "validate_request",
            self._route_after_validation,
            {
                "process": "process_work",
                "error": "handle_error"
            }
        )
        workflow.add_edge("process_work", "generate_response")
        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("handle_error", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    async def _initialize_node(self, state: AgentState) -> AgentState:
        """Initialize the agent workflow state"""
        state["agent_id"] = self.agent_id
        state["agent_type"] = self.agent_type
        state["status"] = "initializing"
        state["metadata"] = {
            "start_time": datetime.now().isoformat(),
            "session_id": str(uuid.uuid4())
        }
        
        self._log_activity("Workflow initialized", {"session_id": state["metadata"]["session_id"]})
        return state
    
    async def _validate_request_node(self, state: AgentState) -> AgentState:
        """Validate incoming work request"""
        try:
            if not state.get("work_order"):
                state["error"] = "No work order provided"
                return state
            
            # Validate work order against agent capabilities
            work_order = state["work_order"]
            if not self._can_handle_task(work_order):
                state["error"] = f"Agent {self.agent_type} cannot handle task {work_order.primary_task}"
                return state
            
            state["status"] = "validated"
            self._log_activity("Request validated", {"task": work_order.primary_task.value})
            return state
            
        except Exception as e:
            state["error"] = f"Validation error: {str(e)}"
            return state
    
    async def _process_work_node(self, state: AgentState) -> AgentState:
        """Process the work request - implemented by subclasses"""
        try:
            state["status"] = "processing"
            
            # This calls the abstract method that subclasses implement
            work_order = state["work_order"]
            result = await self.process_work_request(work_order, state)
            
            state["results"] = result
            state["status"] = "completed"
            
            self._log_activity("Work processing completed", {"result_keys": list(result.keys())})
            return state
            
        except Exception as e:
            state["error"] = f"Processing error: {str(e)}"
            return state
    
    async def _generate_response_node(self, state: AgentState) -> AgentState:
        """Generate structured response using LLM"""
        try:
            if state.get("results"):
                # Create response message
                response_content = self._format_response(state["results"], state["work_order"])
                
                response_message = AIMessage(
                    content=response_content,
                    additional_kwargs={
                        "agent_id": self.agent_id,
                        "agent_type": self.agent_type,
                        "task_completed": True,
                        "results": state["results"]
                    }
                )
                
                state["messages"].append(response_message)
                
            return state
            
        except Exception as e:
            state["error"] = f"Response generation error: {str(e)}"
            return state
    
    async def _handle_error_node(self, state: AgentState) -> AgentState:
        """Handle errors in the workflow"""
        error_msg = state.get("error", "Unknown error")
        state["status"] = "error"
        
        error_message = AIMessage(
            content=f"Error in {self.agent_type}: {error_msg}",
            additional_kwargs={
                "agent_id": self.agent_id,
                "error": True,
                "error_details": error_msg
            }
        )
        
        state["messages"].append(error_message)
        
        self._log_activity("Error handled", {"error": error_msg})
        return state
    
    async def _finalize_node(self, state: AgentState) -> AgentState:
        """Finalize the workflow execution"""
        state["metadata"]["end_time"] = datetime.now().isoformat()
        state["metadata"]["final_status"] = state["status"]
        
        # Store session history
        self.session_history.append({
            "session_id": state["metadata"]["session_id"],
            "start_time": state["metadata"]["start_time"],
            "end_time": state["metadata"]["end_time"],
            "status": state["status"],
            "work_order_id": state["work_order"].order_id if state.get("work_order") else None,
            "results_summary": self._summarize_results(state.get("results"))
        })
        
        self._log_activity("Workflow finalized", {"final_status": state["status"]})
        return state
    
    def _route_after_init(self, state: AgentState) -> str:
        """Route after initialization"""
        return "error" if state.get("error") else "validate"
    
    def _route_after_validation(self, state: AgentState) -> str:
        """Route after validation"""
        return "error" if state.get("error") else "process"
    
    async def process_work_order(self, work_order: WorkOrder) -> Dict[str, Any]:
        """
        Main entry point for processing work orders using LangGraph
        """
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=work_order.processed_query)],
            "work_order": work_order,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": "idle",
            "metadata": {}
        }
        
        # Create thread configuration for checkpointing
        config = {
            "configurable": {
                "thread_id": f"{work_order.order_id}_{self.agent_id}"
            }
        }
        
        # Execute workflow
        final_state = await self.app.ainvoke(initial_state, config=config)
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": final_state["status"],
            "results": final_state.get("results"),
            "error": final_state.get("error"),
            "session_metadata": final_state["metadata"]
        }
    
    async def stream_work_order(self, work_order: WorkOrder):
        """
        Stream work order processing for real-time updates
        """
        initial_state = {
            "messages": [HumanMessage(content=work_order.processed_query)],
            "work_order": work_order,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": "idle",
            "metadata": {}
        }
        
        config = {
            "configurable": {
                "thread_id": f"{work_order.order_id}_{self.agent_id}"
            }
        }
        
        # Stream execution
        async for chunk in self.app.astream(initial_state, config=config):
            yield chunk
    
    def get_workflow_state(self, thread_id: str) -> Dict[str, Any]:
        """Get current workflow state for debugging/monitoring"""
        config = {"configurable": {"thread_id": thread_id}}
        return self.app.get_state(config)
    
    @abstractmethod
    async def process_work_request(self, work_order: WorkOrder, state: AgentState) -> Dict[str, Any]:
        """
        Process a work request and return results.
        Each agent implements this differently based on their specialty.
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return a description of what this agent can do.
        Used by the Project Manager for task delegation.
        """
        pass
    
    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize tools for this agent - override in subclasses"""
        return []
    
    def _can_handle_task(self, work_order: WorkOrder) -> bool:
        """Check if this agent can handle the given work order"""
        return True  # Override in subclasses for specific validation
    
    def _format_response(self, results: Dict[str, Any], work_order: WorkOrder) -> str:
        """Format results into a readable response"""
        return f"Task {work_order.primary_task.value} completed successfully. Results: {results}"
    
    def _summarize_results(self, results: Optional[Dict[str, Any]]) -> str:
        """Create a brief summary of results"""
        if not results:
            return "No results"
        return f"Results with {len(results)} items"
    
    def _log_activity(self, activity: str, details: Dict[str, Any] = None):
        """Log agent activity for debugging and monitoring"""
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "activity": activity,
            "details": details or {}
        }
        
        print(f"[{timestamp}] {self.agent_type}({self.agent_id}): {activity}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}") 