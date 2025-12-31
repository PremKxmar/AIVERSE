"""
AI Career Companion - Supabase Database Service
Handles all database operations using Supabase.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from app.config import settings

logger = logging.getLogger(__name__)

# Supabase client and availability flag
SUPABASE_AVAILABLE = False
Client = None

try:
    from supabase import create_client
    from supabase import Client as SupabaseClient
    Client = SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase not installed. Run: pip install supabase")


class SupabaseService:
    """
    Supabase service for database operations.
    
    Free tier includes:
    - 500MB database
    - 2GB storage
    - 50,000 monthly active users
    - Built-in auth
    """
    
    def __init__(self):
        self.client = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of Supabase client."""
        if self._initialized:
            return
        
        self._initialized = True
        
        if not SUPABASE_AVAILABLE:
            logger.warning("⚠️ Supabase not available - using in-memory storage")
            return
        
        
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_KEY
        
        
        if not url or not key:
            logger.warning("⚠️ Supabase credentials not set - using in-memory storage")
            return
        
        try:
            self.client = create_client(url, key)
            logger.info("✅ Supabase connected successfully")
            
            # Initialize admin client if service role key is available
            self.admin_client = None
            if settings.SUPABASE_SERVICE_ROLE_KEY:
                try:
                    self.admin_client = create_client(url, settings.SUPABASE_SERVICE_ROLE_KEY)
                    logger.info("✅ Supabase Admin client connected")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to connect Supabase Admin client: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            self.client = None
    
    @property
    def is_connected(self) -> bool:
        """Check if Supabase is connected."""
        self._ensure_initialized()
        return self.client is not None
    
    # ============== User Operations ==============
    
    async def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """Create a new user with Supabase Auth."""
        if not self.client:
            return {"error": "Database not connected"}
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            return {"success": True, "user": response.user}
        except Exception as e:
            return {"error": str(e)}
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user."""
        if not self.client:
            return {"error": "Database not connected"}
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True, 
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get current user from token."""
        if not self.client:
            return None
        
        try:
            response = self.client.auth.get_user(access_token)
            return response.user
        except Exception:
            return None
    
    # ============== Profile Operations ==============
    
    async def save_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update user profile."""
        if not self.client:
            return {"error": "Database not connected", "saved": False}
        
        try:
            data = {
                "user_id": user_id,
                "name": profile_data.get("name"),
                "email": profile_data.get("email"),
                "github_username": profile_data.get("github_username"),
                "linkedin_url": profile_data.get("linkedin_url"),
                "skills": profile_data.get("skills", []),
                "experience": profile_data.get("experience", []),
                "education": profile_data.get("education", []),
                "career_goals": profile_data.get("career_goals", []),
                "updated_at": datetime.now().isoformat()
            }
            
            # Upsert (insert or update)
            # Use admin client if available to bypass RLS for initial creation
            client = self.admin_client if self.admin_client else self.client
            response = client.table("profiles").upsert(data).execute()
            
            return {"success": True, "profile": response.data}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        if not self.client:
            return None
        
        try:
            response = self.client.table("profiles").select("*").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None
    
    # ============== Application Tracking ==============
    
    async def save_application(
        self, 
        user_id: str, 
        job_data: Dict[str, Any],
        status: str = "applied"
    ) -> Dict[str, Any]:
        """Save a job application."""
        if not self.client:
            return {"error": "Database not connected"}
        
        try:
            data = {
                "user_id": user_id,
                "job_title": job_data.get("job_title"),
                "company": job_data.get("company"),
                "job_url": job_data.get("job_url"),
                "status": status,
                "applied_at": datetime.now().isoformat(),
                "notes": job_data.get("notes", "")
            }
            
            response = self.client.table("applications").insert(data).execute()
            return {"success": True, "application": response.data}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_applications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all applications for a user."""
        if not self.client:
            return []
        
        try:
            response = self.client.table("applications").select("*").eq("user_id", user_id).order("applied_at", desc=True).execute()
            return response.data
        except Exception:
            return []
    
    async def update_application_status(
        self, 
        application_id: str, 
        status: str
    ) -> Dict[str, Any]:
        """Update application status."""
        if not self.client:
            return {"error": "Database not connected"}
        
        try:
            response = self.client.table("applications").update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", application_id).execute()
            
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    # ============== Learning Progress ==============
    
    async def save_learning_progress(
        self, 
        user_id: str, 
        milestone_id: str,
        progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save learning progress."""
        if not self.client:
            return {"error": "Database not connected"}
        
        try:
            data = {
                "user_id": user_id,
                "milestone_id": milestone_id,
                "completed": progress.get("completed", False),
                "time_spent_minutes": progress.get("time_spent", 0),
                "notes": progress.get("notes", ""),
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.client.table("learning_progress").upsert(data).execute()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_learning_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get learning progress for a user."""
        if not self.client:
            return []
        
        try:
            response = self.client.table("learning_progress").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception:
            return []
    
    # ============== Wellness Tracking ==============
    
    async def log_wellness_check(
        self, 
        user_id: str, 
        wellness_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a wellness check."""
        if not self.client:
            return {"error": "Database not connected"}
        
        try:
            data = {
                "user_id": user_id,
                "mood": wellness_data.get("mood"),
                "energy_level": wellness_data.get("energy_level"),
                "sleep_hours": wellness_data.get("sleep_hours"),
                "stress_level": wellness_data.get("stress_level"),
                "notes": wellness_data.get("notes", ""),
                "logged_at": datetime.now().isoformat()
            }
            
            response = self.client.table("wellness_logs").insert(data).execute()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_wellness_history(
        self, 
        user_id: str, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get wellness history for a user."""
        if not self.client:
            return []
        
        try:
            response = self.client.table("wellness_logs").select("*").eq("user_id", user_id).order("logged_at", desc=True).limit(days).execute()
            return response.data
        except Exception:
            return []


# Singleton instance
_supabase: Optional[SupabaseService] = None

def get_supabase() -> SupabaseService:
    """Get or create Supabase service instance."""
    global _supabase
    if _supabase is None:
        _supabase = SupabaseService()
    return _supabase
