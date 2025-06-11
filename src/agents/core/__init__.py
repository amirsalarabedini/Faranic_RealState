"""
Core agents package for the Faranic Real Estate multi-agent system.
"""

from .base_agent import BaseAgent
from .work_order import WorkOrder, ClientType, TaskType
from .agent_communication import AgentMessage, CommunicationProtocol

__all__ = [
    'BaseAgent',
    'WorkOrder', 
    'ClientType',
    'TaskType',
    'AgentMessage',
    'CommunicationProtocol'
] 