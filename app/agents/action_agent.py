"""
AI Career Companion - Module 4: Action Agent
Opportunity execution - resume tailoring, applications, outreach.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.user_profile import UserProfile
from app.models.events import EventType
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)


class ActionAgent(BaseAgent):
    """
    Module 4: Action Agent (Opportunity Execution)
    
    Responsibilities:
    - Tailor resumes for specific jobs
    - Generate cover letters
    - Draft cold outreach messages
    - Prepare application materials
    - Track application status
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(name="ActionAgent", llm_service=llm_service or get_llm_service())
        logger.info("⚡ Action Agent initialized")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process action requests."""
        action = input_data.get("action", "tailor_resume")
        
        if action == "tailor_resume":
            return await self._tailor_resume(input_data)
        elif action == "generate_cover_letter":
            return await self._generate_cover_letter(input_data)
        elif action == "draft_cold_email":
            return await self._draft_cold_email(input_data)
        elif action == "prepare_application":
            return await self._prepare_application_materials(input_data)
        elif action == "track_application":
            return await self._track_application(input_data)
        elif action == "generate_linkedin_message":
            return await self._generate_linkedin_message(input_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _tailor_resume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tailor a resume for a specific job description.
        """
        profile_data = data.get("profile", {})
        job_description = data.get("job_description", "")
        job_title = data.get("job_title", "")
        company = data.get("company", "")
        
        if not job_description:
            return {"error": "No job description provided"}
        
        self.log_reasoning("tailor_resume", f"Tailoring resume for {job_title} at {company}")
        
        prompt = f"""
Analyze this job description and tailor the resume for maximum ATS score and recruiter appeal.

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{profile_data}

Return JSON:
{{
    "tailored_summary": "2-3 sentence professional summary tailored to this role",
    "keyword_matches": ["keyword1", "keyword2"],
    "keywords_to_add": ["missing but important keywords"],
    "experience_rewrites": [
        {{
            "original": "Original bullet point",
            "tailored": "Tailored version emphasizing relevant skills",
            "added_keywords": ["keywords added"]
        }}
    ],
    "skills_to_highlight": ["Top 5 skills to emphasize"],
    "skills_to_add": ["Relevant skills candidate has but might not have listed"],
    "ats_score_estimate": 85,
    "improvement_tips": ["Specific tips to improve match"]
}}
"""
        
        result = await self.llm.generate_json(prompt, "Resume tailoring suggestions")
        
        # Emit event
        await self.emit_event(EventType.RESUME_TAILORED, {
            "job_title": job_title,
            "company": company,
            "ats_score": result.get("ats_score_estimate", 0) if isinstance(result, dict) else 0
        })
        
        return {
            "success": True,
            "tailoring": result
        }
    
    async def _generate_cover_letter(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized cover letter.
        """
        profile_data = data.get("profile", {})
        job_description = data.get("job_description", "")
        job_title = data.get("job_title", "")
        company = data.get("company", "")
        tone = data.get("tone", "professional")  # professional, casual, enthusiastic
        
        self.log_reasoning("cover_letter", f"Generating cover letter for {job_title} at {company}")
        
        prompt = f"""
Write a compelling cover letter for this application.

JOB: {job_title} at {company}
JOB DESCRIPTION: {job_description[:2000]}

CANDIDATE PROFILE: {profile_data}

TONE: {tone}

Return JSON:
{{
    "cover_letter": "Full cover letter text (3-4 paragraphs)",
    "key_points_highlighted": ["Main selling points used"],
    "company_research_needed": ["Things to research about company to personalize further"],
    "alternative_opening": "Different opening line option"
}}

Make it:
- Specific, not generic
- Show genuine interest in the company
- Highlight 2-3 key achievements
- End with a clear call to action
"""
        
        result = await self.llm.generate_json(prompt, "Cover letter content")
        
        return {
            "success": True,
            "cover_letter": result
        }
    
    async def _draft_cold_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Draft a cold outreach email to a recruiter or hiring manager.
        """
        recipient_role = data.get("recipient_role", "Hiring Manager")
        recipient_name = data.get("recipient_name", "")
        company = data.get("company", "")
        purpose = data.get("purpose", "job inquiry")  # job inquiry, informational interview, referral request
        profile_data = data.get("profile", {})
        
        self.log_reasoning("cold_email", f"Drafting {purpose} email to {recipient_role} at {company}")
        
        prompt = f"""
Draft a cold email for: {purpose}

TO: {recipient_name or recipient_role} at {company}
FROM: A candidate with this background: {profile_data}

Return JSON:
{{
    "subject_lines": ["3 subject line options with open rates"],
    "email_body": "The email body (keep it under 150 words)",
    "call_to_action": "Clear CTA",
    "follow_up_template": "Follow-up email if no response in 1 week",
    "best_time_to_send": "Recommended day/time",
    "tips": ["Tips for better response rate"]
}}

Make it:
- Short and respectful of their time
- Show you've done research
- Have a clear, small ask
- Easy to say yes to
"""
        
        result = await self.llm.generate_json(prompt, "Cold email content")
        
        return {
            "success": True,
            "cold_email": result
        }
    
    async def _prepare_application_materials(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare all application materials for a specific job.
        """
        job_id = data.get("job_id", "")
        job_title = data.get("job_title", "")
        company = data.get("company", "")
        job_description = data.get("job_description", "")
        profile_data = data.get("profile", {})
        
        self.log_reasoning("prepare_application", f"Preparing full application for {job_title}")
        
        # Generate all materials at once
        prompt = f"""
Prepare complete application materials for:
JOB: {job_title} at {company}
JD: {job_description[:2000]}

CANDIDATE: {profile_data}

Return JSON:
{{
    "resume_summary": "Tailored 2-sentence summary",
    "top_skills_to_highlight": ["5 most relevant skills"],
    "experience_bullet_rewrites": [
        "Tailored bullet 1 with metrics",
        "Tailored bullet 2 with keywords"
    ],
    "cover_letter_short": "3-paragraph cover letter",
    "linkedin_headline": "Optimized LinkedIn headline for this role",
    "screening_question_answers": {{
        "Why do you want to work here?": "Answer",
        "What makes you a good fit?": "Answer",
        "Salary expectations?": "Suggested range based on role/location"
    }},
    "company_talking_points": ["3 things to mention about the company"],
    "questions_to_ask": ["3 smart questions for the interview"]
}}
"""
        
        result = await self.llm.generate_json(prompt, "Complete application materials")
        
        await self.emit_event(EventType.APPLICATION_PREPARED, {
            "job_title": job_title,
            "company": company
        })
        
        return {
            "success": True,
            "application_materials": result
        }
    
    async def _track_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track and manage application status.
        """
        application_id = data.get("application_id", "")
        status_update = data.get("status", "")  # applied, viewed, interview, rejected, offer
        notes = data.get("notes", "")
        
        # In production, this would update a database
        # For now, return tracking info
        
        status_stages = {
            "applied": {"next_action": "Wait 5-7 days, then follow up", "emoji": "📬"},
            "viewed": {"next_action": "Prepare for potential interview call", "emoji": "👀"},
            "interview": {"next_action": "Research company, prepare STAR stories", "emoji": "🎯"},
            "rejected": {"next_action": "Request feedback, move to next opportunity", "emoji": "📝"},
            "offer": {"next_action": "Negotiate if needed, celebrate! 🎉", "emoji": "🎉"}
        }
        
        stage_info = status_stages.get(status_update, {"next_action": "Track status", "emoji": "⏳"})
        
        return {
            "success": True,
            "application_id": application_id,
            "status": status_update,
            "emoji": stage_info["emoji"],
            "next_action": stage_info["next_action"],
            "tracked_at": datetime.now().isoformat()
        }
    
    async def _generate_linkedin_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a LinkedIn connection request or InMail.
        """
        recipient_name = data.get("recipient_name", "")
        recipient_title = data.get("recipient_title", "")
        company = data.get("company", "")
        purpose = data.get("purpose", "networking")  # networking, job inquiry, referral
        connection_note = data.get("is_connection_note", True)  # True = 300 char limit
        
        self.log_reasoning("linkedin_message", f"Generating LinkedIn message for {purpose}")
        
        char_limit = 300 if connection_note else 2000
        
        prompt = f"""
Write a LinkedIn {('connection request' if connection_note else 'InMail')} message.

TO: {recipient_name}, {recipient_title} at {company}
PURPOSE: {purpose}
CHARACTER LIMIT: {char_limit}

Return JSON:
{{
    "message": "The message fitting within {char_limit} characters",
    "character_count": 123,
    "alternative_message": "Different approach option",
    "profile_sections_to_update": ["Suggestions to make profile more appealing before sending"]
}}

Make it:
- Personal, not templated
- Show mutual value
- Have a soft but clear ask
- Respect the character limit!
"""
        
        result = await self.llm.generate_json(prompt, "LinkedIn message content")
        
        return {
            "success": True,
            "linkedin_message": result
        }
