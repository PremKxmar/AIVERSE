"""
AI Career Companion - Module 2: Market Oracle Agent
Job market intelligence + India job scraper integration.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from app.agents.base import BaseAgent
from app.models.user_profile import UserProfile
from app.models.job import (
    JobListing, JobAnalysis, SkillGap, TrendingSkill,
    MarketInsight, JobCategory, InternshipListing, HackathonListing
)
from app.models.events import EventType
from app.services.llm_service import LLMService, get_llm_service
from app.config import settings

logger = logging.getLogger(__name__)


# India Job Platforms (from Teammate 2's implementation)
INDIA_JOB_PLATFORMS = {
    "jobs": [
        "linkedin.com", "indeed.com", "glassdoor.com", "naukri.com",
        "shine.com", "foundit.in", "freshersworld.com", "timesjobs.com", "apna.co"
    ],
    "internships": [
        "internshala.com", "letsintern.com", "stipend.com", "linkedin.com",
        "indeed.com", "unstop.com", "freshersworld.com", "twentynineteen.com"
    ],
    "hackathons": [
        "unstop.com", "devpost.com", "hack2skill.com", "hackerearth.com",
        "devfolio.co", "mlh.io", "dare2compete.com", "techgig.com"
    ],
    "courses": [
        "youtube.com", "coursera.org", "udemy.com", "freecodecamp.org",
        "edx.org", "khanacademy.org", "nptel.ac.in", "swayam.gov.in",
        "skillshare.com", "codecademy.com", "geeksforgeeks.org"
    ]
}


class MarketOracleAgent(BaseAgent):
    """
    Module 2: Market Oracle Agent (Job Intelligence)
    
    Responsibilities:
    - Job description analysis ("JD Hard-Truth Scanner")
    - India job platform scraping (40+ sources)
    - Skill trend analysis
    - Role discovery and matching
    - Competitor benchmarking
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(name="MarketOracle", llm_service=llm_service or get_llm_service())
        self.searxng_url = settings.SEARXNG_URL
        logger.info("🔮 Market Oracle Agent initialized")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process market intelligence requests.
        
        Args:
            input_data: Contains 'action' and relevant data
            
        Returns:
            Processing result
        """
        action = input_data.get("action", "analyze_jd")
        
        if action == "analyze_jd":
            return await self._analyze_job_description(input_data)
        elif action == "search_jobs":
            return await self._search_india_jobs(input_data)
        elif action == "search_internships":
            return await self._search_internships(input_data)
        elif action == "search_hackathons":
            return await self._search_hackathons(input_data)
        elif action == "get_trending_skills":
            return await self._get_trending_skills(input_data)
        elif action == "match_jobs":
            return await self._match_jobs_to_profile(input_data)
        elif action == "discover_roles":
            return await self._discover_hidden_roles(input_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _analyze_job_description(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a job description against user profile.
        The "JD Hard-Truth Scanner".
        """
        jd_text = data.get("jd_text", "")
        user_skills = data.get("user_skills", [])
        
        if not jd_text:
            return {"error": "No job description provided"}
        
        self.log_reasoning("analyze_jd", "Parsing job description and extracting requirements")
        
        # Use LLM to analyze JD
        analysis_result = await self.llm.analyze_job_description(jd_text, user_skills)
        
        # Create skill gaps
        skill_gaps = []
        for skill in analysis_result.get("missing_skills", []):
            skill_gaps.append(SkillGap(
                skill_name=skill,
                current_level="missing",
                required_level="intermediate",
                priority=1,
                learning_time_estimate="2 weeks"
            ))
        
        # Create JobAnalysis object
        analysis = JobAnalysis(
            job_title=analysis_result.get("job_title", "Unknown Role"),
            company=analysis_result.get("company"),
            readiness_score=float(analysis_result.get("readiness_score", 0)),
            required_skills=analysis_result.get("required_skills", []),
            preferred_skills=analysis_result.get("preferred_skills", []),
            user_matching_skills=analysis_result.get("matching_skills", []),
            skill_gaps=skill_gaps,
            time_to_ready=analysis_result.get("time_to_ready", "4 weeks"),
            priority_actions=analysis_result.get("priority_actions", []),
            justification=analysis_result.get("justification", "")
        )
        
        # Emit gap detected event if there are skill gaps
        if skill_gaps:
            await self.emit_event(EventType.GAP_DETECTED, {
                "job_title": analysis.job_title,
                "readiness_score": analysis.readiness_score,
                "skill_gaps": [sg.skill_name for sg in skill_gaps]
            })
        
        self.log_reasoning("analyze_jd", 
            f"Analysis complete: {analysis.readiness_score}% ready, {len(skill_gaps)} gaps found")
        
        return {
            "success": True,
            "analysis": analysis.model_dump()
        }
    
    async def _search_india_jobs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for jobs across India platforms.
        Uses SearXNG for meta-search (from Teammate 2's approach).
        """
        query = data.get("query", "")
        location = data.get("location", "India")
        
        if not query:
            return {"error": "No search query provided"}
        
        self.log_reasoning("search_jobs", f"Searching India job platforms for: {query}")
        
        # Generate search queries (like Teammate 2's Planner node)
        search_queries = await self._generate_search_queries(query, "JOB", location)
        
        # Execute searches
        jobs = await self._execute_job_search(search_queries, JobCategory.JOB)
        
        return {
            "success": True,
            "jobs": [job.model_dump() for job in jobs],
            "count": len(jobs),
            "platforms_searched": INDIA_JOB_PLATFORMS["jobs"]
        }
    
    async def _search_internships(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for internships across India platforms.
        """
        query = data.get("query", "")
        
        self.log_reasoning("search_internships", f"Searching internship platforms for: {query}")
        
        search_queries = await self._generate_search_queries(query, "INTERNSHIP", "India")
        jobs = await self._execute_job_search(search_queries, JobCategory.INTERNSHIP)
        
        return {
            "success": True,
            "internships": [job.model_dump() for job in jobs],
            "count": len(jobs)
        }
    
    async def _search_hackathons(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for hackathons.
        """
        query = data.get("query", "hackathon")
        
        self.log_reasoning("search_hackathons", f"Searching hackathon platforms for: {query}")
        
        search_queries = await self._generate_search_queries(query, "HACKATHON", "India")
        
        # For now, return mock data (full implementation would scrape these)
        return {
            "success": True,
            "hackathons": [],
            "count": 0,
            "platforms": INDIA_JOB_PLATFORMS["hackathons"]
        }
    
    async def _generate_search_queries(
        self, 
        base_query: str, 
        category: str, 
        location: str
    ) -> List[str]:
        """
        Generate search queries for different platforms.
        (Inspired by Teammate 2's Planner node)
        """
        platforms = INDIA_JOB_PLATFORMS.get(category.lower() + "s", [])
        
        queries = []
        for platform in platforms[:5]:  # Top 5 platforms
            if category == "JOB":
                queries.append(f"site:{platform} {base_query} jobs {location} 2024")
            elif category == "INTERNSHIP":
                queries.append(f"site:{platform} {base_query} internship {location}")
            elif category == "HACKATHON":
                queries.append(f"site:{platform} {base_query} hackathon 2025")
        
        return queries
    
    async def _execute_job_search(
        self, 
        queries: List[str], 
        category: JobCategory
    ) -> List[JobListing]:
        """
        Execute job searches using SearXNG.
        Returns empty list if SearXNG is not available.
        """
        jobs = []
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                for query in queries[:3]:  # Limit queries
                    try:
                        response = await client.get(
                            f"{self.searxng_url}/search",
                            params={
                                "q": query,
                                "format": "json",
                                "categories": "general"
                            }
                        )
                        if response.status_code == 200:
                            results = response.json().get("results", [])
                            for result in results[:5]:
                                job = self._parse_search_result(result, category)
                                if job:
                                    jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Search query failed: {e}")
                        continue
        except Exception as e:
            logger.warning(f"SearXNG not available: {e}. Start with: docker-compose up -d")
        
        return jobs
    
    def _parse_search_result(self, result: Dict, category: JobCategory) -> Optional[JobListing]:
        """
        Parse a search result into a JobListing.
        """
        try:
            return JobListing(
                role=result.get("title", "Unknown Role"),
                company="Unknown Company",  # Would need scraping to get this
                location="India",
                apply_link=result.get("url", ""),
                source_platform=result.get("engine", "unknown"),
                category=category
            )
        except Exception:
            return None
    

    async def _match_jobs_to_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match jobs against user profile and score them.
        """
        profile_data = data.get("profile")
        jobs_data = data.get("jobs", [])
        
        if not profile_data:
            return {"error": "No profile provided"}
        
        profile = UserProfile(**profile_data)
        user_skill_names = [s.lower() for s in profile.get_skill_names()]
        
        scored_jobs = []
        for job_data in jobs_data:
            job = JobListing(**job_data)
            
            # Calculate match score
            required_skills = [s.lower() for s in job.skills_required]
            matching = set(user_skill_names) & set(required_skills)
            missing = set(required_skills) - set(user_skill_names)
            
            if required_skills:
                match_score = (len(matching) / len(required_skills)) * 100
            else:
                match_score = 50.0  # Default if no skills listed
            
            job.match_score = round(match_score, 1)
            job.matching_skills = list(matching)
            job.missing_skills = list(missing)
            scored_jobs.append(job)
        
        # Sort by match score
        scored_jobs.sort(key=lambda j: j.match_score, reverse=True)
        
        # Emit event for high matches
        high_matches = [j for j in scored_jobs if j.match_score >= 80]
        if high_matches:
            await self.emit_event(EventType.NEW_MATCHES_FOUND, {
                "count": len(high_matches),
                "top_match": high_matches[0].model_dump() if high_matches else None
            })
        
        return {
            "success": True,
            "matched_jobs": [j.model_dump() for j in scored_jobs],
            "high_matches": len(high_matches)
        }
    
    async def _get_trending_skills(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get trending skills in the job market.
        """
        domain = data.get("domain", "software engineering")
        
        self.log_reasoning("trending_skills", f"Analyzing skill trends for: {domain}")
        
        # Use LLM to generate trending skills (in production, would analyze job postings)
        prompt = f"""
List the top 10 trending skills in {domain} for the India job market in 2024-2025.

Return JSON:
[
  {{"skill": "skill name", "growth": 30, "demand": "high", "related_roles": ["role1", "role2"]}}
]

growth = percentage increase in job postings mentioning this skill
demand = low, medium, high
"""
        result = await self.llm.generate_json(prompt, "Array of trending skill objects")
        
        trending = []
        for item in result if isinstance(result, list) else []:
            trending.append(TrendingSkill(
                skill_name=item.get("skill", ""),
                growth_percentage=float(item.get("growth", 0)),
                demand_level=item.get("demand", "medium"),
                related_roles=item.get("related_roles", [])
            ))
        
        return {
            "success": True,
            "trending_skills": [t.model_dump() for t in trending]
        }
    
    async def _discover_hidden_roles(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover roles the user may not know they qualify for.
        """
        profile_data = data.get("profile")
        
        if not profile_data:
            return {"error": "No profile provided"}
        
        profile = UserProfile(**profile_data)
        skills = profile.get_skill_names()
        
        self.log_reasoning("discover_roles", f"Finding hidden roles for skills: {skills[:5]}")
        
        prompt = f"""
Given these skills: {', '.join(skills[:10])}

Suggest 5 job roles the user might not have considered but could qualify for.
Include both traditional and emerging roles.

Return JSON:
[
  {{
    "role": "Role Title",
    "match_reason": "Why they qualify",
    "skill_overlap": ["skill1", "skill2"],
    "growth_potential": "high/medium/low"
  }}
]
"""
        result = await self.llm.generate_json(prompt, "Array of role suggestions")
        
        return {
            "success": True,
            "discovered_roles": result if isinstance(result, list) else []
        }
