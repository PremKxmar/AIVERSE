"""
AI Career Companion - Onboarding Router
Handles user profile creation and management.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.agents.digital_twin import DigitalTwinAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize agent
digital_twin = DigitalTwinAgent()


class ProfileCreateRequest(BaseModel):
    """Profile creation request."""
    name: str
    email: str
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    career_goals: Optional[List[dict]] = None


class SkillOverrideRequest(BaseModel):
    """Manual skill override request."""
    skill_name: str
    level: str  # beginner, intermediate, advanced, expert
    confidence: float = 0.9


@router.post("/onboard")
async def create_profile(request: ProfileCreateRequest):
    """
    Create a new user profile.
    
    Optionally connects GitHub and LinkedIn for enriched profile.
    """
    result = await digital_twin.process({
        "action": "create_profile",
        "name": request.name,
        "email": request.email,
        "github_username": request.github_username,
        "linkedin_url": request.linkedin_url,
        "career_goals": request.career_goals or []
    })
    
    return result


@router.post("/onboard/resume")
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    github_username: Optional[str] = Form(None)
):
    """
    Create profile from resume upload.
    
    Extracts skills, experience, and contact info from PDF.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file bytes
    resume_bytes = await file.read()
    
    result = await digital_twin.process({
        "action": "create_profile",
        "name": name or "Unknown",
        "email": email or "",
        "github_username": github_username,
        "resume_bytes": resume_bytes
    })
    
    return result


@router.post("/profile/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Analyze a resume without creating a profile.
    
    Returns extracted skills and information.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        resume_bytes = await file.read()
        
        logger.info(f"Analyzing resume: {file.filename} ({len(resume_bytes)} bytes)")
        
        result = await digital_twin.process({
            "action": "analyze_resume",
            "resume_bytes": resume_bytes
        })
        
        logger.info("Resume analysis successful")
        return result
    except Exception as e:
        logger.error(f"Resume analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/profile/analyze-github/{username}")
async def analyze_github(username: str):
    """
    Analyze a GitHub profile.
    
    Returns repositories, languages, and detected skills.
    """
    result = await digital_twin.process({
        "action": "analyze_github",
        "username": username
    })
    
    return result


@router.post("/profile/extract-skills")
async def extract_skills(text: str):
    """
    Extract skills from arbitrary text.
    
    Useful for analyzing job descriptions or other documents.
    """
    result = await digital_twin.process({
        "action": "extract_skills",
        "text": text
    })
    
    return result


@router.put("/profile/{profile_id}/skills")
async def override_skill(profile_id: str, request: SkillOverrideRequest):
    """
    Manually override an AI-inferred skill.
    
    Human Override Layer - user has final say over AI inferences.
    """
    # In production, would fetch profile from database
    return {
        "message": f"Skill '{request.skill_name}' updated to {request.level}",
        "profile_id": profile_id,
        "skill": request.model_dump()
    }
