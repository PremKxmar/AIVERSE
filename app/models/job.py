"""
AI Career Companion - Job & Market Models
Module 2: Market Oracle Data Structures
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class JobCategory(str, Enum):
    """Job category types."""
    JOB = "JOB"
    INTERNSHIP = "INTERNSHIP"
    HACKATHON = "HACKATHON"
    COURSE = "COURSE"


class JobType(str, Enum):
    """Employment type."""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class JobListing(BaseModel):
    """
    Job listing scraped from India job platforms.
    Matches the schema from Teammate 2's scraper.
    """
    # Core fields
    role: str
    company: str
    location: str = "India"
    
    # Details
    experience: Optional[str] = None  # "0-2 years"
    salary: Optional[str] = None  # "₹4-8 LPA"
    skills_required: List[str] = []
    job_type: JobType = JobType.FULL_TIME
    
    # Application
    apply_link: str
    posted_date: Optional[str] = None
    application_deadline: Optional[datetime] = None
    
    # Source
    source_platform: str  # naukri, linkedin, internshala, etc.
    category: JobCategory = JobCategory.JOB
    
    # Matching (added after processing)
    match_score: float = 0.0  # 0-100%
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    
    class Config:
        use_enum_values = True


class InternshipListing(BaseModel):
    """Internship-specific fields (extends JobListing concept)."""
    role: str
    company: str
    location: str = "India"
    duration: Optional[str] = None  # "3 months"
    stipend: Optional[str] = None  # "₹10,000/month"
    skills_required: List[str] = []
    start_date: Optional[str] = None
    application_deadline: Optional[str] = None
    perks: List[str] = []  # ["Certificate", "PPO"]
    apply_link: str
    source_platform: str


class HackathonListing(BaseModel):
    """Hackathon event details."""
    event_name: str
    organizer: str
    mode: str = "Online"  # Online, Offline, Hybrid
    location: Optional[str] = None
    dates: Optional[str] = None
    registration_deadline: Optional[str] = None
    themes: List[str] = []
    prizes: Optional[str] = None
    team_size: Optional[str] = None
    eligibility: Optional[str] = None
    registration_link: str
    source_platform: str


class CourseListing(BaseModel):
    """Course/learning resource details."""
    title: str
    platform: str
    instructor: Optional[str] = None
    is_free: bool = True
    price: Optional[str] = None
    duration: Optional[str] = None
    difficulty: str = "Beginner"  # Beginner, Intermediate, Advanced
    rating: Optional[str] = None
    topics_covered: List[str] = []
    certificate: bool = False
    language: str = "English"
    link: str
    source_platform: str


class SkillGap(BaseModel):
    """Identified skill gap between user and target role."""
    skill_name: str
    current_level: str = "missing"  # missing, beginner, intermediate
    required_level: str = "intermediate"
    priority: int = 1  # 1 = highest priority
    learning_time_estimate: str = "2 weeks"
    suggested_resources: List[str] = []


class JobAnalysis(BaseModel):
    """
    Analysis result when user pastes a JD.
    The "JD Hard-Truth Scanner" output.
    """
    job_title: str
    company: Optional[str] = None
    
    # Match scores
    readiness_score: float = 0.0  # 0-100%
    match_breakdown: Dict[str, float] = {}  # {"skills": 70, "experience": 50}
    
    # Skills analysis
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    user_matching_skills: List[str] = []
    skill_gaps: List[SkillGap] = []
    
    # Recommendations
    time_to_ready: str = "4 weeks"  # Estimated time to reach 75% readiness
    priority_actions: List[str] = []  # ["Learn Docker", "Build ML project"]
    
    # AI explanation
    justification: str = ""  # LLM-generated explanation
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)


class TrendingSkill(BaseModel):
    """Skill trend data from market analysis."""
    skill_name: str
    growth_percentage: float  # e.g., 30% more mentions this month
    demand_level: str = "high"  # low, medium, high
    related_roles: List[str] = []
    learning_resources: List[str] = []


class MarketInsight(BaseModel):
    """Aggregated market intelligence."""
    trending_skills: List[TrendingSkill] = []
    declining_skills: List[str] = []  # Skills becoming obsolete
    hot_companies: List[str] = []  # Companies hiring actively
    salary_benchmarks: Dict[str, str] = {}  # {"ML Engineer": "₹12-18 LPA"}
    economic_alerts: List[str] = []  # "Tech layoffs in fintech sector"
    generated_at: datetime = Field(default_factory=datetime.now)
