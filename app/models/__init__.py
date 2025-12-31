"""
AI Career Companion - Data Models Package
"""
from .user_profile import (
    UserProfile,
    Skill,
    Project,
    Education,
    WorkExperience,
)
from .job import (
    JobListing,
    JobAnalysis,
    SkillGap,
)
from .events import AgentEvent

__all__ = [
    "UserProfile",
    "Skill",
    "Project", 
    "Education",
    "WorkExperience",
    "JobListing",
    "JobAnalysis",
    "SkillGap",
    "AgentEvent",
]
