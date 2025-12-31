"""
AI Career Companion - Module 7: Orchestrator Agent
Coordinates all agents, manages state, and routes requests.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.agents.base import BaseAgent
from app.agents.digital_twin import DigitalTwinAgent
from app.agents.market_oracle import MarketOracleAgent
from app.models.events import AgentState, EventType, AgentEvent
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class Phase(str, Enum):
    """Agent workflow phases."""
    IDLE = "idle"
    ONBOARDING = "onboarding"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    ACTING = "acting"
    REFLECTING = "reflecting"


class OrchestratorAgent(BaseAgent):
    """
    Module 7: Orchestrator Agent
    
    Responsibilities:
    - Coordinate agent handoffs
    - Maintain shared state
    - Route requests to appropriate agents
    - Manage autonomy levels
    - Log reasoning chains
    """
    
    def __init__(self):
        super().__init__(name="Orchestrator", llm_service=get_llm_service())
        
        # Initialize child agents
        self.digital_twin = DigitalTwinAgent()
        self.market_oracle = MarketOracleAgent()
        # TODO: Add other agents as implemented
        # self.roadmap_architect = RoadmapArchitectAgent()
        # self.action_agent = ActionAgent()
        # self.evolution_loop = EvolutionLoopAgent()
        # self.go_beyond = GoBeyondAgent()
        
        # State management
        self._sessions: Dict[str, AgentState] = {}
        
        logger.info("🎭 Orchestrator Agent initialized with child agents")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for all requests.
        Routes to appropriate agents based on intent.
        """
        session_id = input_data.get("session_id", "default")
        action = input_data.get("action", "")
        
        # Get or create session state
        state = self._get_or_create_session(session_id)
        
        # Classify intent and route
        intent = await self._classify_intent(action, input_data)
        
        self.log_reasoning("route", f"Intent: {intent}, routing to appropriate agent")
        
        # Route to appropriate agent
        result = await self._route_to_agent(intent, input_data, state)
        
        # Update state
        state.phase = self._get_phase_for_intent(intent)
        
        return result
    
    def _get_or_create_session(self, session_id: str) -> AgentState:
        """Get existing session or create new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = AgentState(session_id=session_id)
            logger.info(f"Created new session: {session_id}")
        return self._sessions[session_id]
    
    async def _classify_intent(self, action: str, data: Dict[str, Any]) -> str:
        """
        Classify user intent from action and data.
        """
        # Direct action mappings
        intent_map = {
            "create_profile": "profile",
            "update_profile": "profile",
            "analyze_resume": "profile",
            "analyze_github": "profile",
            "analyze_jd": "job_analysis",
            "search_jobs": "job_search",
            "search_internships": "job_search",
            "search_hackathons": "job_search",
            "get_trending_skills": "market",
            "match_jobs": "job_matching",
            "discover_roles": "role_discovery",
            "create_roadmap": "roadmap",
            "get_roadmap": "roadmap",
            "complete_milestone": "roadmap",
            "tailor_resume": "action",
            "track_application": "action",
            "analyze_rejection": "feedback",
            "mock_interview": "feedback",
            "check_burnout": "wellness",
        }
        
        if action in intent_map:
            return intent_map[action]
        
        # Use LLM for ambiguous intents
        if data.get("message"):
            return await self._classify_message_intent(data["message"])
        
        return "general"
    
    async def _classify_message_intent(self, message: str) -> str:
        """Use LLM to classify free-form message intent."""
        prompt = f"""
Classify this user message into one category:
- profile: Creating or updating profile
- job_search: Searching for jobs/internships
- job_analysis: Analyzing a specific job description
- roadmap: Learning path and skill development
- action: Resume tailoring, applications
- feedback: Rejections, interviews
- wellness: Burnout, stress
- general: Other questions

Message: "{message}"

Return only the category name, nothing else.
"""
        result = await self.llm.generate(prompt)
        return result.strip().lower()
    
    async def _route_to_agent(
        self, 
        intent: str, 
        data: Dict[str, Any], 
        state: AgentState
    ) -> Dict[str, Any]:
        """Route request to appropriate agent."""
        
        if intent == "profile":
            result = await self.digital_twin.process(data)
            # Store profile in state
            if result.get("profile"):
                state.profile = result["profile"]
            return result
        
        elif intent in ["job_analysis", "job_search", "job_matching", "market", "role_discovery"]:
            # Add profile skills to data if available
            if state.profile:
                data["user_skills"] = state.profile.get("skills", [])
                data["profile"] = state.profile
            return await self.market_oracle.process(data)
        
        elif intent == "roadmap":
            # TODO: Route to Roadmap Architect
            return {"message": "Roadmap agent not yet implemented"}
        
        elif intent == "action":
            # TODO: Route to Action Agent
            return {"message": "Action agent not yet implemented"}
        
        elif intent == "feedback":
            # TODO: Route to Evolution Loop
            return {"message": "Evolution Loop agent not yet implemented"}
        
        elif intent == "wellness":
            # TODO: Route to Go Beyond
            return {"message": "Go Beyond agent not yet implemented"}
        
        else:
            # General conversation - use LLM directly
            return await self._handle_general_query(data, state)
    
    def _get_phase_for_intent(self, intent: str) -> str:
        """Map intent to workflow phase."""
        phase_map = {
            "profile": Phase.ONBOARDING,
            "job_analysis": Phase.ANALYZING,
            "job_search": Phase.ANALYZING,
            "market": Phase.ANALYZING,
            "roadmap": Phase.PLANNING,
            "action": Phase.ACTING,
            "feedback": Phase.REFLECTING,
            "wellness": Phase.REFLECTING,
        }
        return phase_map.get(intent, Phase.IDLE).value
    
    async def _handle_general_query(
        self, 
        data: Dict[str, Any], 
        state: AgentState
    ) -> Dict[str, Any]:
        """Handle general conversation queries."""
        message = data.get("message", "")
        
        # Build context from state
        context = ""
        if state.profile:
            skills = state.profile.get("skills", [])[:5]
            skill_names = [s.get("name", "") if isinstance(s, dict) else s for s in skills]
            context = f"User has these skills: {', '.join(skill_names)}"
        
        prompt = f"""
You are an AI Career Companion helping a user with their career development.

{context}

User: {message}

Provide helpful, actionable career advice. Be encouraging but realistic.
"""
        response = await self.llm.generate(prompt)
        
        # Add to conversation history
        state.messages.append({"role": "user", "content": message})
        state.messages.append({"role": "assistant", "content": response})
        
        return {
            "success": True,
            "response": response
        }
    
    async def handle_event(self, event: AgentEvent) -> Dict[str, Any]:
        """
        Handle inter-agent events.
        Called when agents emit events.
        """
        event_type = event.type
        
        self.log_reasoning("event_handler", f"Processing event: {event_type}")
        
        if event_type == EventType.GAP_DETECTED:
            # Trigger roadmap creation
            return {"action": "create_roadmap", "skill_gaps": event.payload.get("skill_gaps", [])}
        
        elif event_type == EventType.NEW_MATCHES_FOUND:
            # Notify user of new opportunities
            return {"action": "notify_user", "matches": event.payload.get("count", 0)}
        
        elif event_type == EventType.REJECTION_RECEIVED:
            # Trigger rejection analysis
            return {"action": "analyze_rejection", "data": event.payload}
        
        elif event_type == EventType.BURNOUT_DETECTED:
            # Suggest break
            return {"action": "suggest_break", "message": "You seem stressed. Take a break!"}
        
        return {"processed": True}
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state for debugging/monitoring."""
        if session_id in self._sessions:
            return self._sessions[session_id].model_dump()
        return None
    
    def get_reasoning_trace(self, session_id: str) -> List[Dict[str, str]]:
        """Get reasoning trace for transparency."""
        if session_id in self._sessions:
            return self._sessions[session_id].reasoning_trace
        return []
