"""
Agent Communication System - Handles messaging between agents
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class AgentMessage(BaseModel):
    """Standard message format for inter-agent communication"""
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="When message was created")
    
    # Routing information
    sender_agent: str = Field(description="ID of the sending agent")
    recipient_agent: str = Field(description="ID of the receiving agent")
    message_type: str = Field(description="Type of message (request, response, report, etc.)")
    
    # Content
    subject: str = Field(description="Brief subject/title of the message")
    content: Dict[str, Any] = Field(description="Main message content")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Additional data attachments")
    
    # Processing metadata
    priority: str = Field(default="normal", description="Message priority: low, normal, high, urgent")
    requires_response: bool = Field(default=False, description="Whether this message requires a response")
    correlation_id: Optional[str] = Field(None, description="ID linking related messages")
    
    def add_attachment(self, name: str, data: Any, attachment_type: str = "data"):
        """Add an attachment to the message"""
        self.attachments.append({
            "name": name,
            "type": attachment_type,
            "data": data,
            "added_at": datetime.now().isoformat()
        })
    
    def get_attachment(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve an attachment by name"""
        for attachment in self.attachments:
            if attachment["name"] == name:
                return attachment
        return None

class CommunicationProtocol:
    """Manages communication between agents"""
    
    def __init__(self):
        self.message_history: List[AgentMessage] = []
        self.agent_registry: Dict[str, str] = {}  # agent_id -> agent_type
    
    def register_agent(self, agent_id: str, agent_type: str):
        """Register an agent in the communication system"""
        self.agent_registry[agent_id] = agent_type
    
    def send_message(self, message: AgentMessage) -> bool:
        """Send a message between agents"""
        # Validate sender and recipient exist
        if message.sender_agent not in self.agent_registry:
            raise ValueError(f"Sender agent {message.sender_agent} not registered")
        if message.recipient_agent not in self.agent_registry:
            raise ValueError(f"Recipient agent {message.recipient_agent} not registered")
        
        # Add to message history
        self.message_history.append(message)
        return True
    
    def get_messages_for_agent(self, agent_id: str, message_type: Optional[str] = None) -> List[AgentMessage]:
        """Get all messages for a specific agent"""
        messages = [msg for msg in self.message_history if msg.recipient_agent == agent_id]
        
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]
        
        return sorted(messages, key=lambda x: x.timestamp)
    
    def get_conversation_thread(self, correlation_id: str) -> List[AgentMessage]:
        """Get all messages in a conversation thread"""
        return [msg for msg in self.message_history if msg.correlation_id == correlation_id]
    
    def create_work_request(self, sender: str, recipient: str, task: str, work_order_data: Dict[str, Any], priority: str = "normal") -> AgentMessage:
        """Create a standardized work request message"""
        return AgentMessage(
            sender_agent=sender,
            recipient_agent=recipient,
            message_type="work_request",
            subject=f"Work Request: {task}",
            content={
                "task": task,
                "work_order": work_order_data,
                "instructions": f"Please complete the {task} task as specified in the work order."
            },
            priority=priority,
            requires_response=True
        )
    
    def create_report_submission(self, sender: str, recipient: str, report_data: Dict[str, Any], correlation_id: str) -> AgentMessage:
        """Create a standardized report submission message"""
        return AgentMessage(
            sender_agent=sender,
            recipient_agent=recipient,
            message_type="report_submission",
            subject=f"Report from {sender}",
            content={
                "report": report_data,
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            },
            correlation_id=correlation_id,
            requires_response=False
        )
    
    def create_status_update(self, sender: str, recipient: str, status: str, details: str, correlation_id: str) -> AgentMessage:
        """Create a status update message"""
        return AgentMessage(
            sender_agent=sender,
            recipient_agent=recipient,
            message_type="status_update",
            subject=f"Status Update: {status}",
            content={
                "status": status,
                "details": details,
                "updated_at": datetime.now().isoformat()
            },
            correlation_id=correlation_id,
            requires_response=False
        ) 