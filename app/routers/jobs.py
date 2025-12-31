"""
AI Career Companion - Jobs Router
Handles job search, analysis, and matching.
Integrates teammate's India Job Scraper.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
import logging

from app.agents.market_oracle import MarketOracleAgent
from app.services.job_scraper import get_job_scraper, SITE_CONFIGS

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize agents/services
market_oracle = MarketOracleAgent()
job_scraper = get_job_scraper()


class JobSearchRequest(BaseModel):
    """Job search request."""
    query: str
    location: str = "India"
    category: Literal["JOB", "INTERNSHIP", "HACKATHON", "COURSE"] = "JOB"


class JDAnalysisRequest(BaseModel):
    """Job description analysis request."""
    jd_text: str
    user_skills: Optional[List[str]] = None


class JobMatchRequest(BaseModel):
    """Job matching request."""
    profile: Dict[str, Any]
    jobs: Optional[List[Dict[str, Any]]] = None


# ============== India Job Scraper Endpoints (Teammate's Module) ==============

@router.post("/jobs/search-india")
async def search_india_jobs(request: JobSearchRequest):
    """
    🇮🇳 Search for opportunities across 40+ India platforms.
    
    Uses SearXNG + Crawl4AI to scrape real listings from:
    - Jobs: Naukri, LinkedIn, Indeed, Glassdoor, TimesJobs, etc.
    - Internships: Internshala, Unstop, LetsIntern, etc.
    - Hackathons: Unstop, Devpost, HackerEarth, Devfolio, etc.
    - Courses: NPTEL, SWAYAM, Coursera, YouTube, etc.
    """
    result = await job_scraper.search(
        query=request.query,
        category=request.category
    )
    return result


@router.post("/jobs/search")
async def search_jobs(request: JobSearchRequest):
    """
    Search for jobs (uses India scraper for comprehensive results).
    """
    # Use the integrated scraper
    result = await job_scraper.search(
        query=request.query,
        category=request.category
    )
    return result


# ============== Analysis Endpoints ==============

@router.post("/jobs/analyze")
async def analyze_job_description(request: JDAnalysisRequest):
    """
    Analyze a job description.
    
    Returns readiness score, skill gaps, and time to ready.
    This is the "JD Hard-Truth Scanner".
    """
    result = await market_oracle.process({
        "action": "analyze_jd",
        "jd_text": request.jd_text,
        "user_skills": request.user_skills or []
    })
    return result


@router.post("/jobs/match")
async def match_jobs_to_profile(request: JobMatchRequest):
    """
    Match jobs against user profile.
    Returns jobs scored by match percentage.
    """
    result = await market_oracle.process({
        "action": "match_jobs",
        "profile": request.profile,
        "jobs": request.jobs or []
    })
    return result


# ============== Market Intelligence Endpoints ==============

@router.get("/jobs/trending-skills")
async def get_trending_skills(domain: str = "software engineering"):
    """
    Get trending skills in the job market.
    Returns skills with growth percentages and demand levels.
    """
    result = await market_oracle.process({
        "action": "get_trending_skills",
        "domain": domain
    })
    return result


@router.post("/jobs/discover-roles")
async def discover_hidden_roles(profile: Dict[str, Any]):
    """
    Discover roles the user might not know they qualify for.
    Suggests non-obvious career paths based on skills.
    """
    result = await market_oracle.process({
        "action": "discover_roles",
        "profile": profile
    })
    return result


@router.get("/jobs/platforms")
async def list_job_platforms():
    """
    List all 40+ supported India job platforms by category.
    """
    total = sum(len(v["sites"]) for v in SITE_CONFIGS.values())
    
    return {
        "total_platforms": total,
        "categories": {
            category: {
                "sites": config["sites"],
                "count": len(config["sites"]),
                "location_filter": config.get("location_filter")
            }
            for category, config in SITE_CONFIGS.items()
        }
    }


@router.get("/jobs/categories")
async def get_categories():
    """Get available search categories."""
    return {
        "categories": [
            {"id": "JOB", "name": "Jobs", "description": "Full-time job opportunities in India"},
            {"id": "INTERNSHIP", "name": "Internships", "description": "Internship opportunities for students"},
            {"id": "HACKATHON", "name": "Hackathons", "description": "Coding competitions and hackathons"},
            {"id": "COURSE", "name": "Courses", "description": "Educational courses and tutorials"}
        ]
    }
