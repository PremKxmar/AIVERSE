"""
AI Career Companion - LLM Service
Handles all LLM interactions using Google Gemini.
"""
import json
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM Service using Google Gemini.
    Provides structured prompting and response parsing.
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"🤖 LLM Service initialized with {settings.GEMINI_MODEL}")
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = None
    ) -> str:
        """
        Generate text response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Override default temperature
            
        Returns:
            Generated text response
        """
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_TOKENS,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        schema_description: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            prompt: User prompt
            schema_description: Description of expected JSON schema
            system_prompt: Optional system instruction
            
        Returns:
            Parsed JSON response
        """
        json_prompt = f"""
{prompt}

Respond ONLY with valid JSON matching this schema:
{schema_description}

Do not include any text outside the JSON object.
"""
        response = await self.generate(json_prompt, system_prompt)
        
        # Clean and parse JSON
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    
    async def extract_skills_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract skills from resume or project text.
        
        Returns list of {name, level, confidence}
        """
        prompt = f"""
Analyze this text and extract all technical and soft skills mentioned.
For each skill, estimate the proficiency level based on context.

TEXT:
{text[:4000]}  # Truncate for token limits

Return JSON array of skills:
[
  {{"name": "Python", "level": "advanced", "confidence": 0.9}},
  {{"name": "Docker", "level": "intermediate", "confidence": 0.7}},
  ...
]

Levels: beginner, intermediate, advanced, expert
Confidence: 0.0 to 1.0 based on how clearly the skill is demonstrated
"""
        result = await self.generate_json(prompt, "Array of skill objects")
        return result if isinstance(result, list) else []
    
    async def analyze_job_description(
        self, 
        jd_text: str, 
        user_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze a job description against user skills.
        """
        prompt = f"""
Analyze this job description and compare with the user's skills.

JOB DESCRIPTION:
{jd_text[:3000]}

USER'S SKILLS:
{', '.join(user_skills)}

Return JSON:
{{
  "job_title": "extracted job title",
  "company": "company name if mentioned",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "matching_skills": ["skills user has"],
  "missing_skills": ["skills user lacks"],
  "readiness_score": 65,
  "time_to_ready": "4 weeks",
  "priority_actions": ["action1", "action2"],
  "justification": "explanation of the analysis"
}}
"""
        return await self.generate_json(prompt, "Job analysis object")
    
    async def generate_learning_roadmap(
        self,
        skill_gaps: List[str],
        target_role: str,
        timeline_weeks: int = 8
    ) -> Dict[str, Any]:
        """
        Generate a learning roadmap for skill gaps.
        """
        prompt = f"""
Create a {timeline_weeks}-week learning roadmap to prepare for: {target_role}

Skills to learn: {', '.join(skill_gaps)}

Return JSON:
{{
  "total_weeks": {timeline_weeks},
  "milestones": [
    {{
      "week": 1,
      "skill": "skill name",
      "tasks": ["task1", "task2"],
      "resources": ["free resource links"],
      "project": "mini project suggestion"
    }}
  ],
  "final_project": "capstone project suggestion"
}}

Prioritize free resources (YouTube, freeCodeCamp, NPTEL).
Include practical projects for each skill.
"""
        return await self.generate_json(prompt, "Roadmap object")


# Singleton instance
_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
