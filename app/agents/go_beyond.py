"""
AI Career Companion - Module 6: Go Beyond Agent
Wellness, burnout detection, and advanced career features.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.events import EventType
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)


class GoBeyondAgent(BaseAgent):
    """
    Module 6: Go Beyond Agent (Advanced Features)
    
    Responsibilities:
    - Burnout detection and wellness checks
    - Stress monitoring based on activity patterns
    - Weekly digest generation
    - Proactive career alerts
    - Ghost network detection
    - Work-life balance recommendations
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(name="GoBeyond", llm_service=llm_service or get_llm_service())
        logger.info("🚀 Go Beyond Agent initialized")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process go-beyond requests."""
        action = input_data.get("action", "wellness_check")
        
        if action == "wellness_check":
            return await self._wellness_check(input_data)
        elif action == "burnout_assessment":
            return await self._assess_burnout_risk(input_data)
        elif action == "weekly_digest":
            return await self._generate_weekly_digest(input_data)
        elif action == "career_forecast":
            return await self._generate_career_forecast(input_data)
        elif action == "ghost_network_alert":
            return await self._detect_ghost_networks(input_data)
        elif action == "work_life_tips":
            return await self._get_work_life_tips(input_data)
        elif action == "motivation_boost":
            return await self._get_motivation_boost(input_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _wellness_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a wellness check based on user's job search activity.
        """
        daily_hours_searching = data.get("hours_searching", 0)
        rejections_this_week = data.get("rejections", 0)
        days_since_break = data.get("days_since_break", 0)
        mood = data.get("mood", "neutral")  # great, good, neutral, low, struggling
        sleep_hours = data.get("sleep_hours", 7)
        
        self.log_reasoning("wellness_check", f"Performing wellness check (mood: {mood})")
        
        prompt = f"""
Perform a gentle wellness check for someone in a job search:

ACTIVITY DATA:
- Hours spent job searching daily: {daily_hours_searching}
- Rejections this week: {rejections_this_week}
- Days since last break: {days_since_break}
- Current mood reported: {mood}
- Average sleep: {sleep_hours} hours

Return JSON:
{{
    "wellness_score": 75,
    "status": "green/yellow/red",
    "observations": ["What patterns you notice"],
    "concerns": ["Any areas of concern"],
    "recommendations": [
        {{
            "recommendation": "Specific recommendation",
            "why": "Why this helps",
            "how": "How to implement"
        }}
    ],
    "affirmation": "Supportive message",
    "suggested_break_activity": "A specific relaxing activity to try",
    "check_in_reminder": "When to check in again"
}}

Be supportive and non-judgmental. Job searching is hard.
"""
        
        result = await self.llm.generate_json(prompt, "Wellness check results")
        
        # Emit event if concerning
        if isinstance(result, dict) and result.get("status") == "red":
            await self.emit_event(EventType.WELLNESS_ALERT, {
                "wellness_score": result.get("wellness_score"),
                "status": "needs_attention"
            })
        
        return {
            "success": True,
            "wellness": result
        }
    
    async def _assess_burnout_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess burnout risk based on multiple factors.
        """
        activity_log = data.get("activity_log", [])
        job_search_duration_weeks = data.get("weeks_searching", 0)
        interview_to_rejection_ratio = data.get("interview_rejection_ratio", 0)
        self_reported_energy = data.get("energy_level", 5)  # 1-10 scale
        
        self.log_reasoning("burnout_assessment", f"Assessing burnout risk (weeks searching: {job_search_duration_weeks})")
        
        prompt = f"""
Assess burnout risk for this job seeker:

DATA:
- Weeks in job search: {job_search_duration_weeks}
- Interview to rejection ratio: {interview_to_rejection_ratio}
- Self-reported energy (1-10): {self_reported_energy}
- Recent activity: {activity_log}

Return JSON:
{{
    "burnout_risk_level": "low/moderate/high/critical",
    "risk_score": 45,
    "warning_signs": ["Signs of potential burnout detected"],
    "protective_factors": ["Positive factors reducing risk"],
    "immediate_actions": [
        {{
            "action": "What to do now",
            "urgency": "high/medium/low"
        }}
    ],
    "boundary_suggestions": ["Healthy boundaries to set"],
    "resource_recommendations": [
        {{
            "type": "app/article/activity",
            "name": "Specific resource",
            "why": "How it helps"
        }}
    ],
    "perspective_shift": "Reframe to consider"
}}
"""
        
        result = await self.llm.generate_json(prompt, "Burnout assessment")
        
        return {
            "success": True,
            "burnout_assessment": result
        }
    
    async def _generate_weekly_digest(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a weekly career digest with personalized insights.
        """
        profile_data = data.get("profile", {})
        target_roles = data.get("target_roles", [])
        skills = data.get("skills", [])
        
        self.log_reasoning("weekly_digest", "Generating personalized weekly digest")
        
        prompt = f"""
Create a personalized weekly career digest:

USER INTERESTS:
- Target roles: {target_roles}
- Skills: {skills[:10]}

Return JSON:
{{
    "digest_title": "This Week in {target_roles[0] if target_roles else 'Tech'}",
    "market_pulse": {{
        "hot_roles": ["Roles seeing increased hiring"],
        "cooling_roles": ["Roles seeing decreased hiring"],
        "emerging_skills": ["Skills trending up"]
    }},
    "opportunities_to_watch": [
        {{
            "type": "job/hackathon/event/course",
            "title": "Opportunity name",
            "why_relevant": "Why this matches their profile",
            "deadline": "If applicable"
        }}
    ],
    "learning_spotlight": {{
        "skill_of_the_week": "Skill to focus on",
        "why_now": "Why this skill is timely",
        "quick_resource": "Free resource to start"
    }},
    "motivation_corner": {{
        "quote": "Relevant motivational quote",
        "success_story": "Brief inspiring story",
        "tip_of_the_week": "Practical career tip"
    }},
    "next_week_focus": "What to prioritize next week"
}}
"""
        
        result = await self.llm.generate_json(prompt, "Weekly digest")
        
        return {
            "success": True,
            "weekly_digest": result
        }
    
    async def _generate_career_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a career forecast based on trends and user profile.
        """
        profile_data = data.get("profile", {})
        current_role = data.get("current_role", "")
        target_role = data.get("target_role", "")
        
        self.log_reasoning("career_forecast", f"Generating forecast for {target_role or current_role}")
        
        prompt = f"""
Generate a career forecast:

CURRENT ROLE: {current_role}
TARGET ROLE: {target_role}
PROFILE: {profile_data}

Return JSON:
{{
    "forecast_period": "Next 12-18 months",
    "role_outlook": {{
        "demand_trend": "increasing/stable/decreasing",
        "salary_trend": "Salary outlook",
        "remote_opportunities": "Remote work availability"
    }},
    "skills_forecast": [
        {{
            "skill": "Skill name",
            "trend": "rising/stable/declining",
            "recommendation": "What to do about it"
        }}
    ],
    "career_paths": [
        {{
            "path": "Career path option",
            "timeline": "Estimated timeline",
            "steps": ["Key steps to take"]
        }}
    ],
    "industry_shifts": ["Major industry changes to watch"],
    "opportunities": ["Emerging opportunities to consider"],
    "risks": ["Risks to be aware of"]
}}
"""
        
        result = await self.llm.generate_json(prompt, "Career forecast")
        
        return {
            "success": True,
            "forecast": result
        }
    
    async def _detect_ghost_networks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential ghost networks in user's job applications.
        Ghost networks = companies that post jobs but rarely hire external candidates.
        """
        applications = data.get("applications", [])
        
        self.log_reasoning("ghost_networks", "Analyzing application patterns")
        
        # In production, this would analyze actual response patterns
        prompt = f"""
Analyze these job applications for potential "ghost network" patterns:

APPLICATIONS: {applications}

Ghost networks are companies that:
- Post jobs but rarely hire externally
- Have positions open for very long
- Never respond to qualified candidates

Return JSON:
{{
    "potential_ghost_networks": [
        {{
            "company": "Company name",
            "warning_signs": ["Why this might be a ghost network"],
            "recommendation": "What to do"
        }}
    ],
    "healthy_applications": ["Companies that seem responsive"],
    "optimization_tips": ["Tips to avoid wasting time on ghost networks"],
    "red_flags_to_watch": ["General signs of a ghost posting"]
}}
"""
        
        result = await self.llm.generate_json(prompt, "Ghost network analysis")
        
        return {
            "success": True,
            "ghost_network_analysis": result
        }
    
    async def _get_work_life_tips(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get work-life balance tips during job search.
        """
        situation = data.get("situation", "active job search")
        challenges = data.get("challenges", [])
        
        prompt = f"""
Provide work-life balance tips for someone in:

SITUATION: {situation}
CHALLENGES: {challenges}

Return JSON:
{{
    "daily_structure": {{
        "job_search_hours": "Recommended focused hours",
        "break_schedule": "When to take breaks",
        "cutoff_time": "When to stop for the day"
    }},
    "boundary_tips": [
        {{
            "boundary": "Specific boundary to set",
            "how": "How to implement it"
        }}
    ],
    "self_care_practices": ["Daily self-care suggestions"],
    "productivity_hacks": ["Tips to search smarter not harder"],
    "social_connection": "Tips to stay connected during job search"
}}
"""
        
        result = await self.llm.generate_json(prompt, "Work-life tips")
        
        return {
            "success": True,
            "work_life_tips": result
        }
    
    async def _get_motivation_boost(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a personalized motivation boost.
        """
        current_mood = data.get("mood", "neutral")
        recent_setback = data.get("setback", "")
        
        self.log_reasoning("motivation", f"Generating motivation boost for {current_mood} mood")
        
        prompt = f"""
Provide a motivation boost for someone feeling {current_mood}.

Recent setback if any: {recent_setback}

Return JSON:
{{
    "personalized_message": "Warm, encouraging message",
    "perspective_reframe": "A new way to look at their situation",
    "micro_win_suggestion": "A tiny achievable win they can get today",
    "success_reminder": "Reminder of how far they've come",
    "inspiration": {{
        "quote": "Relevant quote",
        "story": "Brief inspiring story"
    }},
    "action_prompt": "One small action to take right now"
}}

Be genuine and supportive, not cheesy or generic.
"""
        
        result = await self.llm.generate_json(prompt, "Motivation boost")
        
        return {
            "success": True,
            "motivation_boost": result
        }
