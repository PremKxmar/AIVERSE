"""
AI Career Companion - User Profile Models
Module 1: Digital Twin Data Structures
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillSource(str, Enum):
    """Where the skill was detected from."""
    RESUME = "resume"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    MANUAL = "manual"
    INFERRED = "inferred"


class Skill(BaseModel):
    """Individual skill with metadata."""
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    source: SkillSource = SkillSource.MANUAL
    embedding: Optional[List[float]] = None  # 384-dim vector
    last_used: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class Project(BaseModel):
    """User project (from GitHub or manual entry)."""
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    technologies: List[str] = []
    stars: int = 0
    commits: int = 0
    readme_quality: Optional[float] = None  # 0-1 score
    source: str = "manual"  # github, manual, resume


class Education(BaseModel):
    """Educational background."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    is_current: bool = False


class WorkExperience(BaseModel):
    """Work experience entry."""
    company: str
    title: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    skills_used: List[str] = []
    achievements: List[str] = []


class CareerGoal(BaseModel):
    """User's career goal."""
    target_role: str
    target_companies: List[str] = []
    target_salary: Optional[str] = None
    timeline_weeks: int = 12
    priority: int = 1  # 1 = highest


class ContextualMemory(BaseModel):
    """Remembered context about the user (struggles, strengths, etc.)."""
    struggles: List[str] = []  # "Struggled with system design"
    strengths: List[str] = []  # "Strong at Python"
    interview_stress_points: List[str] = []
    past_rejections: List[Dict[str, Any]] = []
    preferences: Dict[str, Any] = {}  # Learning style, notification prefs


class UserProfile(BaseModel):
    """
    Complete user profile - The "Digital Twin".
    This is the central data structure used by all agents.
    """
    # Identity
    id: Optional[str] = None
    name: str
    email: str
    
    # Professional Profile
    skills: List[Skill] = []
    skill_embeddings: Optional[List[float]] = None  # Aggregated embedding
    projects: List[Project] = []
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    
    # Career
    career_goals: List[CareerGoal] = []
    years_of_experience: int = 0
    job_readiness_score: float = 0.0  # 0-100%
    
    # External profiles
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_text: Optional[str] = None
    
    # Memory
    contextual_memory: ContextualMemory = Field(default_factory=ContextualMemory)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    profile_version: int = 1
    
    def get_skill_names(self) -> List[str]:
        """Get list of skill names."""
        return [skill.name for skill in self.skills]
    
    def get_top_skills(self, n: int = 5) -> List[Skill]:
        """Get top N skills by confidence."""
        sorted_skills = sorted(self.skills, key=lambda s: s.confidence, reverse=True)
        return sorted_skills[:n]
    
    def add_skill(self, skill: Skill) -> None:
        """Add or update a skill."""
        existing = next((s for s in self.skills if s.name.lower() == skill.name.lower()), None)
        if existing:
            # Update existing skill if new confidence is higher
            if skill.confidence > existing.confidence:
                self.skills.remove(existing)
                self.skills.append(skill)
        else:
            self.skills.append(skill)
        self.updated_at = datetime.now()


class ProfileSummary(BaseModel):
    """Lightweight profile summary for quick operations."""
    id: str
    name: str
    top_skills: List[str]
    years_of_experience: int
    job_readiness_score: float
    primary_goal: Optional[str] = None
