"""
AI Career Companion - Event Models
Inter-agent communication events.
"""
from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Types of events agents can emit."""
    # Profile events
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    SKILLS_EXTRACTED = "skills_extracted"
    
    # Job events
    GAP_DETECTED = "gap_detected"
    JOB_ANALYZED = "job_analyzed"
    NEW_MATCHES_FOUND = "new_matches_found"
    
    # Roadmap events
    ROADMAP_CREATED = "roadmap_created"
    ROADMAP_UPDATED = "roadmap_updated"
    MILESTONE_COMPLETED = "milestone_completed"
    
    # Application events
    APPLICATION_SUBMITTED = "application_submitted"
    DEADLINE_APPROACHING = "deadline_approaching"
    
    # Feedback events
    REJECTION_RECEIVED = "rejection_received"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    OFFER_RECEIVED = "offer_received"
    
    # Wellness events
    BURNOUT_DETECTED = "burnout_detected"
    WEEKLY_DIGEST_READY = "weekly_digest_ready"


class AgentEvent(BaseModel):
    """
    Event emitted by agents for inter-agent communication.
    Published to Redis streams and consumed by Orchestrator.
    """
    id: Optional[str] = None
    type: EventType
    source_agent: str
    target_agent: Optional[str] = None  # None = broadcast
    payload: Dict[str, Any] = {}
    priority: int = 1  # 1 = highest
    timestamp: datetime = Field(default_factory=datetime.now)
    processed: bool = False
    
    class Config:
        use_enum_values = True


class AgentState(BaseModel):
    """
    Shared state passed between agents in LangGraph workflow.
    This is the central state object for the orchestrator.
    """
    # Session
    session_id: str
    user_id: Optional[str] = None
    
    # Current phase
    phase: str = "idle"  # idle, onboarding, analyzing, planning, acting, reflecting
    
    # User data
    profile: Optional[Dict[str, Any]] = None
    skill_embeddings: Optional[list] = None
    
    # Job context
    target_job: Optional[Dict[str, Any]] = None
    required_skills: List[str] = []
    skill_gaps: List[Dict[str, Any]] = []
    
    # Roadmap
    roadmap_steps: List[Dict[str, Any]] = []
    current_step: int = 0
    
    # Matching
    job_matches: List[Dict[str, Any]] = []
    readiness_score: float = 0.0
    
    # Communication
    messages: List[Dict[str, str]] = []  # Chat history
    pending_response: Optional[str] = None
    
    # Events
    events_queue: List[AgentEvent] = []
    
    # Reasoning trace (for transparency)
    reasoning_trace: List[Dict[str, str]] = []
    
    def add_reasoning(self, agent: str, thought: str) -> None:
        """Add a reasoning step to the trace."""
        self.reasoning_trace.append({
            "agent": agent,
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        })
