"""
AI Career Companion - Module 3: Roadmap Architect Agent
Adaptive Skill Learning Path Planner.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.agents.base import BaseAgent
from app.models.user_profile import UserProfile, Skill
from app.models.events import EventType
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)


class LearningResource:
    """Represents a learning resource."""
    def __init__(
        self,
        title: str,
        resource_type: str,  # video, article, course, project
        url: str,
        platform: str,
        duration: str,
        difficulty: str,
        is_free: bool = True
    ):
        self.title = title
        self.resource_type = resource_type
        self.url = url
        self.platform = platform
        self.duration = duration
        self.difficulty = difficulty
        self.is_free = is_free
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "type": self.resource_type,
            "url": self.url,
            "platform": self.platform,
            "duration": self.duration,
            "difficulty": self.difficulty,
            "is_free": self.is_free
        }


class LearningMilestone:
    """Represents a milestone in the learning roadmap."""
    def __init__(
        self,
        name: str,
        description: str,
        skills: List[str],
        duration_days: int,
        resources: List[LearningResource],
        deliverable: str
    ):
        self.name = name
        self.description = description
        self.skills = skills
        self.duration_days = duration_days
        self.resources = resources
        self.deliverable = deliverable
        self.completed = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "skills": self.skills,
            "duration_days": self.duration_days,
            "resources": [r.to_dict() for r in self.resources],
            "deliverable": self.deliverable,
            "completed": self.completed
        }


class RoadmapArchitectAgent(BaseAgent):
    """
    Module 3: Roadmap Architect Agent
    
    Responsibilities:
    - Generate personalized learning roadmaps
    - Recommend resources (courses, videos, projects)
    - Create micro-learning schedules
    - Track progress and adapt recommendations
    - Integrate with skill gap analysis
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(name="RoadmapArchitect", llm_service=llm_service or get_llm_service())
        logger.info("🗺️ Roadmap Architect Agent initialized")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process roadmap requests."""
        action = input_data.get("action", "generate_roadmap")
        
        if action == "generate_roadmap":
            return await self._generate_learning_roadmap(input_data)
        elif action == "get_daily_tasks":
            return await self._get_daily_learning_tasks(input_data)
        elif action == "find_resources":
            return await self._find_learning_resources(input_data)
        elif action == "update_progress":
            return await self._update_learning_progress(input_data)
        elif action == "get_micro_learning":
            return await self._get_micro_learning_content(input_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _generate_learning_roadmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized learning roadmap based on skill gaps.
        """
        skill_gaps = data.get("skill_gaps", [])
        target_role = data.get("target_role", "")
        available_hours_per_week = data.get("hours_per_week", 10)
        learning_style = data.get("learning_style", "balanced")  # video, reading, hands-on, balanced
        
        if not skill_gaps and not target_role:
            return {"error": "Provide skill_gaps or target_role"}
        
        self.log_reasoning("generate_roadmap", f"Creating roadmap for: {target_role or skill_gaps}")
        
        # Use LLM to generate roadmap structure
        prompt = f"""
Create a personalized learning roadmap for someone aiming to become a {target_role or 'skilled developer'}.

Skills to learn/improve: {', '.join(skill_gaps) if skill_gaps else 'Based on target role'}
Available time: {available_hours_per_week} hours per week
Learning preference: {learning_style}

Return a JSON object with this structure:
{{
    "roadmap_name": "Path to {target_role}",
    "total_duration_weeks": 12,
    "milestones": [
        {{
            "name": "Milestone 1: Foundations",
            "description": "Build core fundamentals",
            "week_start": 1,
            "week_end": 3,
            "skills": ["skill1", "skill2"],
            "resources": [
                {{
                    "title": "Course/Video name",
                    "type": "course/video/article/project",
                    "platform": "YouTube/Coursera/etc",
                    "url": "https://example.com",
                    "duration": "4 hours",
                    "is_free": true
                }}
            ],
            "deliverable": "Complete a mini-project demonstrating these skills"
        }}
    ],
    "daily_commitment": "2 hours",
    "success_criteria": "What success looks like"
}}

Include 4-6 milestones with realistic timeframes. Focus on FREE resources from:
- YouTube (freeCodeCamp, Traversy Media, Fireship, etc.)
- GeeksforGeeks, W3Schools
- NPTEL, SWAYAM (India govt)
- Free Coursera/edX courses
"""
        
        result = await self.llm.generate_json(prompt, "Roadmap object")
        
        if not isinstance(result, dict):
            result = {"error": "Failed to generate roadmap"}
        
        # Emit roadmap created event
        await self.emit_event(EventType.ROADMAP_CREATED, {
            "roadmap_name": result.get("roadmap_name", "Learning Path"),
            "total_weeks": result.get("total_duration_weeks", 12),
            "milestones_count": len(result.get("milestones", []))
        })
        
        return {
            "success": True,
            "roadmap": result
        }
    
    async def _get_daily_learning_tasks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get today's micro-learning tasks based on current progress.
        """
        current_milestone = data.get("current_milestone", "")
        available_minutes = data.get("available_minutes", 30)
        
        self.log_reasoning("daily_tasks", f"Generating {available_minutes}min tasks for: {current_milestone}")
        
        prompt = f"""
Create a focused learning plan for today based on:
- Current milestone: {current_milestone or 'General skill building'}
- Available time: {available_minutes} minutes

Return JSON:
{{
    "date": "{datetime.now().strftime('%Y-%m-%d')}",
    "theme": "Today's focus area",
    "tasks": [
        {{
            "task": "Task description",
            "duration_minutes": 10,
            "type": "watch/read/practice/build",
            "resource_url": "https://...",
            "completed": false
        }}
    ],
    "motivation_tip": "Encouraging message",
    "streak_bonus": "Bonus activity if extra time"
}}

Keep tasks SHORT and achievable. Include mix of theory + practice.
"""
        
        result = await self.llm.generate_json(prompt, "Daily tasks object")
        
        return {
            "success": True,
            "daily_plan": result
        }
    
    async def _find_learning_resources(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find learning resources for a specific skill.
        """
        skill = data.get("skill", "")
        resource_type = data.get("type", "all")  # video, course, article, project
        difficulty = data.get("difficulty", "beginner")
        free_only = data.get("free_only", True)
        
        if not skill:
            return {"error": "No skill specified"}
        
        self.log_reasoning("find_resources", f"Finding {resource_type} resources for: {skill}")
        
        prompt = f"""
Find the best learning resources for: {skill}
Level: {difficulty}
Type preference: {resource_type}
Free only: {free_only}

Return JSON array of 10 resources:
[
    {{
        "title": "Resource name",
        "type": "video/course/article/project/documentation",
        "platform": "YouTube/Coursera/GeeksforGeeks/NPTEL/etc",
        "url": "Direct URL",
        "duration": "Estimated time",
        "difficulty": "beginner/intermediate/advanced",
        "rating": "Highly recommended/Good/Okay",
        "why_recommended": "Brief reason",
        "is_free": true
    }}
]

Prioritize:
1. YouTube tutorials (freeCodeCamp, Traversy, Fireship, CodeWithHarry for Hindi)
2. Official documentation
3. Free courses on Coursera/NPTEL/SWAYAM
4. Interactive platforms (freeCodeCamp, Codecademy free tier)
5. Project-based learning resources
"""
        
        result = await self.llm.generate_json(prompt, "Array of resources")
        
        return {
            "success": True,
            "skill": skill,
            "resources": result if isinstance(result, list) else []
        }
    
    async def _update_learning_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update learning progress and get next recommendations.
        """
        completed_task = data.get("completed_task", "")
        milestone_id = data.get("milestone_id", "")
        time_spent_minutes = data.get("time_spent", 0)
        difficulty_feedback = data.get("difficulty", "just_right")  # too_easy, just_right, too_hard
        
        self.log_reasoning("update_progress", f"Recording progress: {completed_task}")
        
        # Generate encouragement and next steps
        prompt = f"""
A learner just completed: {completed_task}
Time spent: {time_spent_minutes} minutes
Their feedback: {difficulty_feedback}

Provide:
{{
    "celebration_message": "Brief 🎉 celebration",
    "xp_earned": 50,
    "streak_status": "You're on a 3-day streak!",
    "next_recommended": {{
        "task": "What to do next",
        "reason": "Why this is the logical next step"
    }},
    "adjustment": "If too_hard/too_easy, suggest pace adjustment"
}}
"""
        
        result = await self.llm.generate_json(prompt, "Progress update response")
        
        # Emit progress event
        await self.emit_event(EventType.LEARNING_COMPLETED, {
            "task": completed_task,
            "time_spent": time_spent_minutes
        })
        
        return {
            "success": True,
            "progress_update": result
        }
    
    async def _get_micro_learning_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get micro-learning content for quick sessions (5-15 mins).
        """
        topic = data.get("topic", "programming")
        time_available = data.get("minutes", 10)
        format_preference = data.get("format", "any")  # video, flashcard, quiz, tip
        
        self.log_reasoning("micro_learning", f"Generating {time_available}min content for: {topic}")
        
        prompt = f"""
Create micro-learning content for a {time_available}-minute session on: {topic}
Format: {format_preference}

Return:
{{
    "content_type": "flashcards/quiz/tip/video_summary",
    "title": "Quick Learn: {topic}",
    "content": [
        {{
            "type": "flashcard/question/tip",
            "front": "Question or concept",
            "back": "Answer or explanation",
            "example": "Code example if applicable"
        }}
    ],
    "quick_takeaway": "One key thing to remember",
    "practice_prompt": "Try this small exercise"
}}

Make it engaging and memorable!
"""
        
        result = await self.llm.generate_json(prompt, "Micro-learning content")
        
        return {
            "success": True,
            "micro_learning": result
        }
