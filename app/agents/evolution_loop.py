"""
AI Career Companion - Module 5: Evolution Loop Agent
Continuous feedback, rejection analysis, and interview prep.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.events import EventType
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)


class EvolutionLoopAgent(BaseAgent):
    """
    Module 5: Evolution Loop Agent
    
    Responsibilities:
    - Analyze rejections and extract learnings
    - Mock interview practice
    - Interview question preparation
    - Feedback incorporation
    - Continuous profile improvement suggestions
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(name="EvolutionLoop", llm_service=llm_service or get_llm_service())
        logger.info("🔄 Evolution Loop Agent initialized")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process evolution loop requests."""
        action = input_data.get("action", "analyze_rejection")
        
        if action == "analyze_rejection":
            return await self._analyze_rejection(input_data)
        elif action == "mock_interview":
            return await self._conduct_mock_interview(input_data)
        elif action == "generate_interview_questions":
            return await self._generate_interview_questions(input_data)
        elif action == "evaluate_answer":
            return await self._evaluate_interview_answer(input_data)
        elif action == "weekly_review":
            return await self._generate_weekly_review(input_data)
        elif action == "improvement_suggestions":
            return await self._get_improvement_suggestions(input_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _analyze_rejection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a job rejection and extract actionable insights.
        The "Rejection Autopsy" feature.
        """
        job_title = data.get("job_title", "")
        company = data.get("company", "")
        rejection_message = data.get("rejection_message", "")
        stage_rejected = data.get("stage", "")  # application, phone screen, technical, final
        profile_data = data.get("profile", {})
        
        self.log_reasoning("analyze_rejection", f"Analyzing rejection from {company}")
        
        prompt = f"""
Perform a constructive "rejection autopsy" for this application:

ROLE: {job_title} at {company}
STAGE REJECTED: {stage_rejected or 'Unknown'}
REJECTION MESSAGE: {rejection_message or 'No specific feedback provided'}

CANDIDATE PROFILE: {profile_data}

Return JSON:
{{
    "likely_reasons": [
        {{
            "reason": "Specific likely reason",
            "confidence": "high/medium/low",
            "evidence": "Why you think this"
        }}
    ],
    "skill_gaps_indicated": ["Skills that might have been missing"],
    "actionable_improvements": [
        {{
            "improvement": "What to improve",
            "how": "Specific action to take",
            "timeline": "How long it might take"
        }}
    ],
    "silver_lining": "Something positive to take from this",
    "similar_roles_to_target": ["Alternative roles that might be better fits"],
    "motivation_message": "Encouraging message to keep going"
}}

Be honest but constructive. This is about growth, not blame.
"""
        
        result = await self.llm.generate_json(prompt, "Rejection analysis")
        
        # Emit event for learning tracking
        await self.emit_event(EventType.REJECTION_ANALYZED, {
            "company": company,
            "job_title": job_title,
            "stage": stage_rejected
        })
        
        return {
            "success": True,
            "rejection_analysis": result
        }
    
    async def _conduct_mock_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a mock interview session.
        """
        job_title = data.get("job_title", "Software Developer")
        company = data.get("company", "")
        interview_type = data.get("type", "behavioral")  # behavioral, technical, hr, case
        difficulty = data.get("difficulty", "medium")
        profile_data = data.get("profile", {})
        
        self.log_reasoning("mock_interview", f"Preparing {interview_type} mock interview for {job_title}")
        
        prompt = f"""
Create a mock interview session for:
ROLE: {job_title} at {company or 'a tech company'}
TYPE: {interview_type} interview
DIFFICULTY: {difficulty}

CANDIDATE BACKGROUND: {profile_data}

Return JSON:
{{
    "interview_intro": "Brief intro the interviewer would give",
    "questions": [
        {{
            "question": "Interview question",
            "type": "behavioral/technical/situational",
            "what_they_look_for": "What the interviewer wants to hear",
            "sample_strong_answer": "Example of a strong answer",
            "common_mistakes": ["Mistakes to avoid"],
            "follow_up_questions": ["Potential follow-ups"]
        }}
    ],
    "closing_section": {{
        "how_to_close_strong": "Tips for closing the interview",
        "questions_to_ask_them": ["Smart questions to ask"]
    }},
    "overall_tips": ["Key tips for this type of interview"]
}}

Include 5-7 questions progressing in difficulty.
"""
        
        result = await self.llm.generate_json(prompt, "Mock interview content")
        
        return {
            "success": True,
            "mock_interview": result
        }
    
    async def _generate_interview_questions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate likely interview questions for a specific role.
        """
        job_title = data.get("job_title", "")
        company = data.get("company", "")
        job_description = data.get("job_description", "")
        interview_round = data.get("round", "general")
        
        self.log_reasoning("interview_questions", f"Generating questions for {job_title} at {company}")
        
        prompt = f"""
Generate likely interview questions for:
ROLE: {job_title} at {company}
ROUND: {interview_round}
JD: {job_description[:1500] if job_description else 'Standard role'}

Return JSON:
{{
    "company_specific": [
        {{
            "question": "Question specific to this company/role",
            "why_asked": "Why they might ask this",
            "preparation_tip": "How to prepare"
        }}
    ],
    "technical_questions": [
        {{
            "question": "Technical question",
            "difficulty": "easy/medium/hard",
            "topics_covered": ["relevant topics"],
            "approach_tip": "How to approach this"
        }}
    ],
    "behavioral_questions": [
        {{
            "question": "Behavioral question",
            "star_tip": "How to structure answer using STAR"
        }}
    ],
    "curveball_questions": [
        {{
            "question": "Unexpected question they might ask",
            "purpose": "What they're testing"
        }}
    ],
    "questions_you_should_ask": ["Impressive questions to ask them"]
}}

Include 15-20 questions total.
"""
        
        result = await self.llm.generate_json(prompt, "Interview questions")
        
        return {
            "success": True,
            "interview_questions": result
        }
    
    async def _evaluate_interview_answer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a user's answer to an interview question.
        """
        question = data.get("question", "")
        user_answer = data.get("answer", "")
        job_title = data.get("job_title", "")
        
        self.log_reasoning("evaluate_answer", f"Evaluating answer to: {question[:50]}...")
        
        prompt = f"""
Evaluate this interview answer:

QUESTION: {question}
CANDIDATE'S ANSWER: {user_answer}
ROLE: {job_title or 'Software Developer'}

Return JSON:
{{
    "score": 7,
    "score_breakdown": {{
        "clarity": 8,
        "relevance": 7,
        "structure": 6,
        "confidence": 7
    }},
    "strengths": ["What was good about the answer"],
    "improvements": ["Specific improvements needed"],
    "improved_version": "A better version of their answer",
    "key_points_missed": ["Important points they could have mentioned"],
    "delivery_tips": ["Tips for how to deliver this better"]
}}

Be constructive and specific. Score out of 10.
"""
        
        result = await self.llm.generate_json(prompt, "Answer evaluation")
        
        return {
            "success": True,
            "evaluation": result
        }
    
    async def _generate_weekly_review(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a weekly progress review and recommendations.
        """
        activities = data.get("activities", [])  # List of activities done this week
        applications_sent = data.get("applications", 0)
        interviews = data.get("interviews", 0)
        learning_hours = data.get("learning_hours", 0)
        
        self.log_reasoning("weekly_review", "Generating weekly career progress review")
        
        prompt = f"""
Generate a weekly career progress review:

THIS WEEK'S ACTIVITY:
- Applications sent: {applications_sent}
- Interviews attended: {interviews}
- Learning hours: {learning_hours}
- Activities: {activities}

Return JSON:
{{
    "week_summary": "Brief summary of the week",
    "wins": ["Celebrations and achievements"],
    "areas_to_improve": ["Areas needing attention"],
    "next_week_priorities": [
        {{
            "priority": "What to focus on",
            "why": "Why this matters",
            "action": "Specific action to take"
        }}
    ],
    "motivation_score": 8,
    "burnout_risk": "low/medium/high",
    "encouragement": "Personalized encouragement based on their week"
}}
"""
        
        result = await self.llm.generate_json(prompt, "Weekly review")
        
        return {
            "success": True,
            "weekly_review": result
        }
    
    async def _get_improvement_suggestions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized improvement suggestions based on history.
        """
        rejection_count = data.get("rejections", 0)
        interview_feedback = data.get("interview_feedback", [])
        profile_data = data.get("profile", {})
        
        prompt = f"""
Provide personalized improvement suggestions:

PROFILE: {profile_data}
REJECTIONS: {rejection_count}
INTERVIEW FEEDBACK: {interview_feedback}

Return JSON:
{{
    "top_3_improvements": [
        {{
            "area": "Improvement area",
            "current_state": "Where they are now",
            "target_state": "Where they should be",
            "action_plan": "How to get there",
            "resources": ["Helpful resources"]
        }}
    ],
    "quick_wins": ["Easy improvements that have big impact"],
    "long_term_investments": ["Skills worth investing time in"],
    "mindset_shift": "Mental reframe that could help"
}}
"""
        
        result = await self.llm.generate_json(prompt, "Improvement suggestions")
        
        return {
            "success": True,
            "suggestions": result
        }
