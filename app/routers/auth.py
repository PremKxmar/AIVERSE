"""
AI Career Companion - Auth Router
Handles user authentication with Supabase.
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Lazy import to avoid startup errors with supabase
def _get_supabase_service():
    try:
        from app.services.supabase_service import get_supabase
        return get_supabase()
    except Exception as e:
        logger.warning(f"Supabase not available: {e}")
        return None


class SignUpRequest(BaseModel):
    """Sign up request."""
    email: str
    password: str
    name: str


class SignInRequest(BaseModel):
    """Sign in request."""
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    """Profile update request."""
    name: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[list] = None
    career_goals: Optional[list] = None


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """Dependency to get current user from auth header."""
    if not authorization:
        return None
    
    supabase = _get_supabase_service()
    if not supabase:
        return None
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    token = parts[1]
    return await supabase.get_current_user(token)


# ============== Auth Endpoints ==============

@router.post("/auth/signup")
async def sign_up(request: SignUpRequest):
    """Create a new user account."""
    supabase = _get_supabase_service()
    
    if not supabase or not supabase.is_connected:
        return {"error": "Database not connected. Add SUPABASE_URL and SUPABASE_KEY to .env"}
    
    logger.info(f"Attempting signup for: {request.email}")
    result = await supabase.create_user(request.email, request.password)
    
    if "error" in result:
        logger.error(f"Signup failed: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Create profile with name
    if result.get("user"):
        user_id = result["user"].id
        logger.info(f"User created: {user_id}. Attempting to create profile...")
        
        # Try to save profile
        profile_result = await supabase.save_profile(user_id, {
            "name": request.name,
            "email": request.email
        })
        
        if profile_result.get("error"):
            logger.error(f"Profile creation failed: {profile_result['error']}")
            # Don't fail the request, but log it. The trigger might have handled it.
        else:
            logger.info("Profile created successfully via API")
    
    return {
        "success": True,
        "message": "Account created! Please check your email to verify.",
        "user_id": result["user"].id if result.get("user") else None
    }


@router.post("/auth/signin")
async def sign_in(request: SignInRequest):
    """Sign in to an existing account."""
    supabase = _get_supabase_service()
    
    if not supabase or not supabase.is_connected:
        return {"error": "Database not connected. Add SUPABASE_URL and SUPABASE_KEY to .env"}
    
    result = await supabase.sign_in(request.email, request.password)
    
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return {
        "success": True,
        "access_token": result["session"].access_token if result.get("session") else None,
        "user": {
            "id": result["user"].id,
            "email": result["user"].email
        } if result.get("user") else None
    }


@router.get("/auth/me")
async def get_me(authorization: Optional[str] = Header(None)):
    """Get current user profile."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    profile = await supabase.get_profile(user.id) if supabase else None
    
    return {
        "user": {"id": user.id, "email": user.email},
        "profile": profile
    }


@router.put("/auth/profile")
async def update_profile(request: ProfileUpdateRequest, authorization: Optional[str] = Header(None)):
    """Update user profile."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    if not supabase:
        return {"error": "Database not connected"}
    
    update_data = request.model_dump(exclude_none=True)
    result = await supabase.save_profile(user.id, update_data)
    return result


# ============== Application Tracking ==============

@router.post("/user/applications")
async def save_application(
    job_title: str,
    company: str,
    job_url: str = "",
    notes: str = "",
    authorization: Optional[str] = Header(None)
):
    """Save a job application."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    if not supabase:
        return {"error": "Database not connected"}
    
    result = await supabase.save_application(user.id, {
        "job_title": job_title,
        "company": company,
        "job_url": job_url,
        "notes": notes
    })
    return result


@router.get("/user/applications")
async def get_applications(authorization: Optional[str] = Header(None)):
    """Get all user applications."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    applications = await supabase.get_applications(user.id) if supabase else []
    return {"applications": applications}


@router.put("/user/applications/{application_id}")
async def update_application(
    application_id: str,
    status: str,
    authorization: Optional[str] = Header(None)
):
    """Update application status."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    if not supabase:
        return {"error": "Database not connected"}
    
    result = await supabase.update_application_status(application_id, status)
    return result


# ============== Wellness Logging ==============

@router.post("/user/wellness")
async def log_wellness(
    mood: str,
    energy_level: int = 5,
    sleep_hours: float = 7,
    stress_level: int = 5,
    notes: str = "",
    authorization: Optional[str] = Header(None)
):
    """Log a wellness check-in."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    if not supabase:
        return {"error": "Database not connected"}
    
    result = await supabase.log_wellness_check(user.id, {
        "mood": mood,
        "energy_level": energy_level,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "notes": notes
    })
    return result


@router.get("/user/wellness")
async def get_wellness_history(days: int = 7, authorization: Optional[str] = Header(None)):
    """Get wellness history."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    history = await supabase.get_wellness_history(user.id, days) if supabase else []
    return {"wellness_history": history}


# ============== Learning Progress ==============

@router.post("/user/progress")
async def save_progress(
    milestone_id: str,
    completed: bool = False,
    time_spent: int = 0,
    notes: str = "",
    authorization: Optional[str] = Header(None)
):
    """Save learning progress."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    if not supabase:
        return {"error": "Database not connected"}
    
    result = await supabase.save_learning_progress(user.id, milestone_id, {
        "completed": completed,
        "time_spent": time_spent,
        "notes": notes
    })
    return result


@router.get("/user/progress")
async def get_progress(authorization: Optional[str] = Header(None)):
    """Get learning progress."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = _get_supabase_service()
    progress = await supabase.get_learning_progress(user.id) if supabase else []
    return {"progress": progress}
