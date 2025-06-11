"""
Base Agent Class - Foundation for all specialist agents
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import uuid
import asyncio
from datetime import datetime

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.configs.llm_config import get_default_llm
from .agent_communication import AgentMessage, CommunicationProtocol
from .work_order import WorkOrder

class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents in the system.
    Provides common functionality and enforces interface consistency.
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type or self.__class__.__name__
        self.llm = get_default_llm()
        self.communication: Optional[CommunicationProtocol] = None
        self.status = "idle"
        self.current_tasks: Dict[str, Any] = {}
        
    def register_communication(self, communication_protocol: CommunicationProtocol):
        """Register with the communication system"""
        self.communication = communication_protocol
        self.communication.register_agent(self.agent_id, self.agent_type)
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to another agent"""
        if not self.communication:
            raise RuntimeError("Agent not registered with communication protocol")
        return self.communication.send_message(message)
    
    async def get_messages(self, message_type: Optional[str] = None) -> List[AgentMessage]:
        """Get messages for this agent"""
        if not self.communication:
            raise RuntimeError("Agent not registered with communication protocol")
        return self.communication.get_messages_for_agent(self.agent_id, message_type)
    
    async def send_status_update(self, recipient: str, status: str, details: str, correlation_id: str):
        """Send a status update to another agent"""
        message = self.communication.create_status_update(
            sender=self.agent_id,
            recipient=recipient,
            status=status,
            details=details,
            correlation_id=correlation_id
        )
        await self.send_message(message)
    
    async def send_report(self, recipient: str, report_data: Dict[str, Any], correlation_id: str):
        """Send a completed report to another agent"""
        message = self.communication.create_report_submission(
            sender=self.agent_id,
            recipient=recipient,
            report_data=report_data,
            correlation_id=correlation_id
        )
        await self.send_message(message)
    
    @abstractmethod
    async def process_work_request(self, work_order: WorkOrder, request_message: AgentMessage) -> Dict[str, Any]:
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
    
    async def handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """
        Main message handler - routes different message types to appropriate methods
        """
        try:
            if message.message_type == "work_request":
                work_order_data = message.content.get("work_order", {})
                work_order = WorkOrder(**work_order_data)
                
                # Update status
                await self.send_status_update(
                    recipient=message.sender_agent,
                    status="processing",
                    details=f"Started processing work request: {message.subject}",
                    correlation_id=message.correlation_id
                )
                
                # Process the work
                result = await self.process_work_request(work_order, message)
                
                # Send the result back
                await self.send_report(
                    recipient=message.sender_agent,
                    report_data=result,
                    correlation_id=message.correlation_id
                )
                
                return result
                
            elif message.message_type == "status_request":
                return {
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type,
                    "status": self.status,
                    "current_tasks": list(self.current_tasks.keys()),
                    "capabilities": self.get_capabilities()
                }
            
            else:
                return await self.handle_custom_message(message)
                
        except Exception as e:
            # Send error status
            await self.send_status_update(
                recipient=message.sender_agent,
                status="error",
                details=f"Error processing message: {str(e)}",
                correlation_id=message.correlation_id
            )
            raise e
    
    async def handle_custom_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """
        Handle custom message types. Override in subclasses if needed.
        """
        return None
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None):
        """Log agent activity for debugging and monitoring"""
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "activity": activity,
            "details": details or {}
        }
        # TODO: Implement proper logging system
        print(f"[{timestamp}] {self.agent_type}({self.agent_id}): {activity}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
    
    async def start_listening(self):
        """
        Start the agent's message processing loop.
        This method runs continuously to process incoming messages.
        """
        self.log_activity("Agent started listening for messages")
        
        while True:
            try:
                # Get new messages
                messages = await self.get_messages()
                
                # Process each message
                for message in messages:
                    if message.message_id not in self.current_tasks:
                        self.current_tasks[message.message_id] = "processing"
                        
                        # Process message asynchronously
                        asyncio.create_task(self._process_message_safely(message))
                
                # Sleep briefly before checking for new messages
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                self.log_activity("Agent stopped by user")
                break
            except Exception as e:
                self.log_activity("Error in message processing loop", {"error": str(e)})
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_message_safely(self, message: AgentMessage):
        """Safely process a message with error handling"""
        try:
            await self.handle_message(message)
            self.current_tasks.pop(message.message_id, None)
        except Exception as e:
            self.log_activity("Error processing message", {
                "message_id": message.message_id,
                "error": str(e)
            })
            self.current_tasks.pop(message.message_id, None) 