"""
AI Career Companion - Base Agent Class
All agents inherit from this base class.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI Career Companion agents.
    
    Provides common functionality:
    - State management
    - Logging
    - LLM integration
    - Event emission
    """
    
    def __init__(self, name: str, llm_service=None):
        self.name = name
        self.llm = llm_service
        self.created_at = datetime.now()
        self._state: Dict[str, Any] = {}
        logger.info(f"🤖 Agent initialized: {self.name}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method. Must be implemented by each agent.
        
        Args:
            input_data: Input data for the agent to process
            
        Returns:
            Processed output data
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return self._state.copy()
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update agent state."""
        self._state.update(updates)
        logger.debug(f"[{self.name}] State updated: {list(updates.keys())}")
    
    async def emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Emit an event for other agents to consume.
        Events are published to Redis streams.
        """
        event = {
            "type": event_type,
            "source": self.name,
            "timestamp": datetime.now().isoformat(),
            "payload": payload
        }
        logger.info(f"[{self.name}] Event emitted: {event_type}")
        # TODO: Publish to Redis stream
        return event
    
    async def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call LLM with the given prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        if self.llm is None:
            raise ValueError(f"[{self.name}] LLM service not configured")
        return await self.llm.generate(prompt, system_prompt)
    
    def log_reasoning(self, step: str, reasoning: str) -> None:
        """Log reasoning step for transparency."""
        logger.info(f"[{self.name}] 💭 {step}: {reasoning}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
