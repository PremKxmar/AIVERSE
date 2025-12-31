"""
AI Career Companion - Module 1: Digital Twin Agent
Handles user profile creation, skill extraction, and persistent memory.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.user_profile import (
    UserProfile, Skill, Project, Education, 
    WorkExperience, SkillLevel, SkillSource, CareerGoal
)
from app.models.events import EventType
from app.services.llm_service import LLMService, get_llm_service
from app.services.pdf_parser import PDFParserService, get_pdf_parser
from app.services.github_analyzer import GitHubAnalyzerService, get_github_analyzer

logger = logging.getLogger(__name__)


class DigitalTwinAgent(BaseAgent):
    """
    Module 1: Digital Twin Agent (User Profile & Memory)
    
    Responsibilities:
    - Multi-source onboarding (Resume, GitHub, LinkedIn)
    - Skill extraction and vectorization
    - Profile maintenance and versioning
    - Contextual memory management
    """
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        pdf_parser: Optional[PDFParserService] = None,
        github_analyzer: Optional[GitHubAnalyzerService] = None
    ):
        super().__init__(name="DigitalTwin", llm_service=llm_service or get_llm_service())
        self.pdf_parser = pdf_parser or get_pdf_parser()
        self.github_analyzer = github_analyzer or get_github_analyzer()
        logger.info("🧬 Digital Twin Agent initialized")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user data and create/update profile.
        
        Args:
            input_data: Contains 'action' and relevant data
            
        Returns:
            Processing result with updated profile
        """
        action = input_data.get("action", "create_profile")
        
        if action == "create_profile":
            return await self._create_profile(input_data)
        elif action == "update_profile":
            return await self._update_profile(input_data)
        elif action == "analyze_resume":
            return await self._analyze_resume(input_data)
        elif action == "analyze_github":
            return await self._analyze_github(input_data)
        elif action == "extract_skills":
            return await self._extract_skills(input_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _create_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user profile from multiple sources.
        """
        self.log_reasoning("create_profile", "Starting profile creation from provided data")
        
        profile = UserProfile(
            name=data.get("name", "Unknown"),
            email=data.get("email", ""),
            github_username=data.get("github_username"),
            linkedin_url=data.get("linkedin_url"),
        )
        
        # Process resume if provided
        if "resume_bytes" in data:
            self.log_reasoning("create_profile", "Extracting data from resume PDF")
            resume_result = await self._analyze_resume({
                "resume_bytes": data["resume_bytes"]
            })
            
            if "skills" in resume_result:
                for skill_data in resume_result["skills"]:
                    skill = Skill(
                        name=skill_data["name"],
                        level=SkillLevel(skill_data.get("level", "intermediate")),
                        confidence=skill_data.get("confidence", 0.7),
                        source=SkillSource.RESUME
                    )
                    profile.add_skill(skill)
            
            profile.resume_text = resume_result.get("text", "")
            
            # Extract contact info
            if resume_result.get("contact"):
                if resume_result["contact"].get("name"):
                    profile.name = resume_result["contact"]["name"]
                if resume_result["contact"].get("email"):
                    profile.email = resume_result["contact"]["email"]
        
        # Analyze GitHub if provided
        if data.get("github_username"):
            self.log_reasoning("create_profile", f"Analyzing GitHub profile: {data['github_username']}")
            github_result = await self._analyze_github({
                "username": data["github_username"]
            })
            
            if "skills_detected" in github_result:
                for skill_name in github_result["skills_detected"]:
                    skill = Skill(
                        name=skill_name,
                        level=SkillLevel.INTERMEDIATE,
                        confidence=0.8,
                        source=SkillSource.GITHUB
                    )
                    profile.add_skill(skill)
            
            # Add projects from GitHub
            for repo in github_result.get("repositories", [])[:5]:
                project = Project(
                    name=repo["name"],
                    description=repo.get("description"),
                    url=repo.get("url"),
                    technologies=[repo.get("language")] if repo.get("language") else [],
                    stars=repo.get("stars", 0),
                    source="github"
                )
                profile.projects.append(project)
        
        # Set career goals if provided
        if data.get("career_goals"):
            for goal in data["career_goals"]:
                profile.career_goals.append(CareerGoal(
                    target_role=goal.get("role", "Software Engineer"),
                    timeline_weeks=goal.get("timeline_weeks", 12)
                ))
        
        # Calculate initial job readiness score
        profile.job_readiness_score = self._calculate_readiness_score(profile)
        
        # Emit profile created event
        await self.emit_event(EventType.PROFILE_CREATED, {
            "profile_id": profile.id,
            "skill_count": len(profile.skills),
            "project_count": len(profile.projects)
        })
        
        self.log_reasoning("create_profile", 
            f"Profile created with {len(profile.skills)} skills and {len(profile.projects)} projects")
        
        return {
            "success": True,
            "profile": profile.model_dump(),
            "summary": {
                "skills_found": len(profile.skills),
                "projects_found": len(profile.projects),
                "readiness_score": profile.job_readiness_score
            }
        }
    
    async def _analyze_resume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume PDF and extract structured data.
        """
        self.log_reasoning("analyze_resume", "Extracting text from resume PDF")
        
        # Extract text from PDF
        if "resume_bytes" in data:
            text = self.pdf_parser.extract_text_from_bytes(data["resume_bytes"])
        elif "file_path" in data:
            text = self.pdf_parser.extract_text(data["file_path"])
        else:
            return {"error": "No resume provided"}
        
        # Extract contact info
        contact = self.pdf_parser.extract_contact_info(text)
        
        # Extract sections
        sections = self.pdf_parser.extract_sections(text)
        
        # Use LLM to extract skills
        self.log_reasoning("analyze_resume", "Using LLM to extract skills from resume text")
        skills = await self.llm.extract_skills_from_text(text)
        
        return {
            "text": text,
            "contact": contact,
            "sections": sections,
            "skills": skills
        }
    
    async def _analyze_github(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GitHub profile.
        """
        username = data.get("username")
        if not username:
            return {"error": "No GitHub username provided"}
        
        self.log_reasoning("analyze_github", f"Analyzing GitHub profile: {username}")
        return await self.github_analyzer.analyze_user(username)
    
    async def _extract_skills(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract skills from arbitrary text.
        """
        text = data.get("text", "")
        if not text:
            return {"error": "No text provided"}
        
        skills = await self.llm.extract_skills_from_text(text)
        return {"skills": skills}
    
    async def _update_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing profile with new data.
        """
        profile_data = data.get("profile")
        updates = data.get("updates", {})
        
        if not profile_data:
            return {"error": "No profile provided"}
        
        profile = UserProfile(**profile_data)
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now()
        profile.profile_version += 1
        
        await self.emit_event(EventType.PROFILE_UPDATED, {
            "profile_id": profile.id,
            "updates": list(updates.keys())
        })
        
        return {
            "success": True,
            "profile": profile.model_dump()
        }
    
    def _calculate_readiness_score(self, profile: UserProfile) -> float:
        """
        Calculate job readiness score based on profile completeness.
        """
        score = 0.0
        
        # Skills (40%)
        skill_count = len(profile.skills)
        score += min(40, skill_count * 5)
        
        # Projects (25%)
        project_count = len(profile.projects)
        score += min(25, project_count * 5)
        
        # Education (15%)
        if profile.education:
            score += 15
        
        # Work experience (15%)
        if profile.work_experience:
            score += 15
        
        # Career goals (5%)
        if profile.career_goals:
            score += 5
        
        return min(100, score)
    
    async def add_contextual_memory(
        self, 
        profile: UserProfile, 
        memory_type: str, 
        content: str
    ) -> UserProfile:
        """
        Add a contextual memory to the profile.
        
        Args:
            profile: User profile
            memory_type: 'struggle', 'strength', 'interview_stress', etc.
            content: Memory content
            
        Returns:
            Updated profile
        """
        if memory_type == "struggle":
            profile.contextual_memory.struggles.append(content)
        elif memory_type == "strength":
            profile.contextual_memory.strengths.append(content)
        elif memory_type == "interview_stress":
            profile.contextual_memory.interview_stress_points.append(content)
        
        profile.updated_at = datetime.now()
        return profile
