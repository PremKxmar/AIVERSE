"""
AI Career Companion - Career Development Router
Handles roadmap, actions, evolution, and wellness endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from app.agents.roadmap_architect import RoadmapArchitectAgent
from app.agents.action_agent import ActionAgent
from app.agents.evolution_loop import EvolutionLoopAgent
from app.agents.go_beyond import GoBeyondAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize agents
roadmap_agent = RoadmapArchitectAgent()
action_agent = ActionAgent()
evolution_agent = EvolutionLoopAgent()
go_beyond_agent = GoBeyondAgent()


# ============== Request Models ==============

class RoadmapRequest(BaseModel):
    """Request for learning roadmap generation."""
    skill_gaps: List[str] = []
    target_role: str = ""
    hours_per_week: int = 10
    learning_style: str = "balanced"


class ResourceRequest(BaseModel):
    """Request for learning resources."""
    skill: str
    type: str = "all"
    difficulty: str = "beginner"
    free_only: bool = True


class ResumeRequest(BaseModel):
    """Request for resume tailoring."""
    profile: Dict[str, Any]
    job_description: str
    job_title: str = ""
    company: str = ""


class CoverLetterRequest(BaseModel):
    """Request for cover letter generation."""
    profile: Dict[str, Any]
    job_description: str
    job_title: str
    company: str
    tone: str = "professional"


class InterviewRequest(BaseModel):
    """Request for mock interview."""
    job_title: str
    company: str = ""
    type: str = "behavioral"
    difficulty: str = "medium"
    profile: Dict[str, Any] = {}


class RejectionRequest(BaseModel):
    """Request for rejection analysis."""
    job_title: str
    company: str
    rejection_message: str = ""
    stage: str = ""
    profile: Dict[str, Any] = {}


class WellnessRequest(BaseModel):
    """Request for wellness check."""
    hours_searching: int = 0
    rejections: int = 0
    days_since_break: int = 0
    mood: str = "neutral"
    sleep_hours: int = 7


# ============== Roadmap Endpoints (Module 3) ==============

@router.post("/roadmap/generate")
async def generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap.
    
    Creates milestones, resources, and timeline based on skill gaps.
    """
    result = await roadmap_agent.process({
        "action": "generate_roadmap",
        "skill_gaps": request.skill_gaps,
        "target_role": request.target_role,
        "hours_per_week": request.hours_per_week,
        "learning_style": request.learning_style
    })
    return result


@router.get("/roadmap/daily")
async def get_daily_tasks(
    current_milestone: str = "",
    available_minutes: int = 30
):
    """Get today's micro-learning tasks."""
    result = await roadmap_agent.process({
        "action": "get_daily_tasks",
        "current_milestone": current_milestone,
        "available_minutes": available_minutes
    })
    return result


@router.post("/roadmap/resources")
async def find_resources(request: ResourceRequest):
    """Find learning resources for a specific skill."""
    result = await roadmap_agent.process({
        "action": "find_resources",
        "skill": request.skill,
        "type": request.type,
        "difficulty": request.difficulty,
        "free_only": request.free_only
    })
    return result


@router.get("/roadmap/micro-learning")
async def get_micro_learning(topic: str = "programming", minutes: int = 10):
    """Get micro-learning content for quick sessions."""
    result = await roadmap_agent.process({
        "action": "get_micro_learning",
        "topic": topic,
        "minutes": minutes
    })
    return result


# ============== Action Endpoints (Module 4) ==============

@router.post("/action/tailor-resume")
async def tailor_resume(request: ResumeRequest):
    """
    Tailor resume for a specific job.
    
    Analyzes JD and suggests optimizations for ATS and recruiter appeal.
    """
    result = await action_agent.process({
        "action": "tailor_resume",
        "profile": request.profile,
        "job_description": request.job_description,
        "job_title": request.job_title,
        "company": request.company
    })
    return result


@router.post("/action/cover-letter")
async def generate_cover_letter(request: CoverLetterRequest):
    """Generate a personalized cover letter."""
    result = await action_agent.process({
        "action": "generate_cover_letter",
        "profile": request.profile,
        "job_description": request.job_description,
        "job_title": request.job_title,
        "company": request.company,
        "tone": request.tone
    })
    return result


@router.post("/action/cold-email")
async def draft_cold_email(
    recipient_role: str,
    company: str,
    purpose: str = "job inquiry",
    recipient_name: str = "",
    profile: Dict[str, Any] = {}
):
    """Draft a cold outreach email."""
    result = await action_agent.process({
        "action": "draft_cold_email",
        "recipient_role": recipient_role,
        "recipient_name": recipient_name,
        "company": company,
        "purpose": purpose,
        "profile": profile
    })
    return result


@router.post("/action/linkedin-message")
async def generate_linkedin_message(
    recipient_name: str,
    recipient_title: str,
    company: str,
    purpose: str = "networking",
    is_connection_note: bool = True
):
    """Generate LinkedIn connection request or InMail."""
    result = await action_agent.process({
        "action": "generate_linkedin_message",
        "recipient_name": recipient_name,
        "recipient_title": recipient_title,
        "company": company,
        "purpose": purpose,
        "is_connection_note": is_connection_note
    })
    return result


# ============== Evolution Endpoints (Module 5) ==============

@router.post("/evolution/analyze-rejection")
async def analyze_rejection(request: RejectionRequest):
    """
    Analyze a job rejection and extract insights.
    
    The "Rejection Autopsy" feature for learning from setbacks.
    """
    result = await evolution_agent.process({
        "action": "analyze_rejection",
        "job_title": request.job_title,
        "company": request.company,
        "rejection_message": request.rejection_message,
        "stage": request.stage,
        "profile": request.profile
    })
    return result


@router.post("/evolution/mock-interview")
async def mock_interview(request: InterviewRequest):
    """Conduct a mock interview session."""
    result = await evolution_agent.process({
        "action": "mock_interview",
        "job_title": request.job_title,
        "company": request.company,
        "type": request.type,
        "difficulty": request.difficulty,
        "profile": request.profile
    })
    return result


@router.post("/evolution/interview-questions")
async def get_interview_questions(
    job_title: str,
    company: str = "",
    job_description: str = "",
    round: str = "general"
):
    """Generate likely interview questions for a role."""
    result = await evolution_agent.process({
        "action": "generate_interview_questions",
        "job_title": job_title,
        "company": company,
        "job_description": job_description,
        "round": round
    })
    return result


@router.post("/evolution/evaluate-answer")
async def evaluate_answer(
    question: str,
    answer: str,
    job_title: str = ""
):
    """Evaluate an interview answer and get feedback."""
    result = await evolution_agent.process({
        "action": "evaluate_answer",
        "question": question,
        "answer": answer,
        "job_title": job_title
    })
    return result


@router.get("/evolution/weekly-review")
async def weekly_review(
    applications: int = 0,
    interviews: int = 0,
    learning_hours: int = 0
):
    """Generate weekly progress review."""
    result = await evolution_agent.process({
        "action": "weekly_review",
        "applications": applications,
        "interviews": interviews,
        "learning_hours": learning_hours
    })
    return result


# ============== Go Beyond Endpoints (Module 6) ==============

@router.post("/wellness/check")
async def wellness_check(request: WellnessRequest):
    """
    Perform a wellness check.
    
    Monitors job search stress and provides recommendations.
    """
    result = await go_beyond_agent.process({
        "action": "wellness_check",
        "hours_searching": request.hours_searching,
        "rejections": request.rejections,
        "days_since_break": request.days_since_break,
        "mood": request.mood,
        "sleep_hours": request.sleep_hours
    })
    return result


@router.post("/wellness/burnout-assessment")
async def burnout_assessment(
    weeks_searching: int = 0,
    interview_rejection_ratio: float = 0,
    energy_level: int = 5
):
    """Assess burnout risk based on activity patterns."""
    result = await go_beyond_agent.process({
        "action": "burnout_assessment",
        "weeks_searching": weeks_searching,
        "interview_rejection_ratio": interview_rejection_ratio,
        "energy_level": energy_level
    })
    return result


@router.get("/wellness/motivation")
async def get_motivation(mood: str = "neutral", setback: str = ""):
    """Get a personalized motivation boost."""
    result = await go_beyond_agent.process({
        "action": "motivation_boost",
        "mood": mood,
        "setback": setback
    })
    return result


@router.get("/career/weekly-digest")
async def weekly_digest(
    target_roles: List[str] = [],
    skills: List[str] = []
):
    """Get personalized weekly career digest."""
    result = await go_beyond_agent.process({
        "action": "weekly_digest",
        "target_roles": target_roles,
        "skills": skills
    })
    return result


@router.get("/career/forecast")
async def career_forecast(
    current_role: str = "",
    target_role: str = ""
):
    """Get career forecast based on trends."""
    result = await go_beyond_agent.process({
        "action": "career_forecast",
        "current_role": current_role,
        "target_role": target_role
    })
    return result
