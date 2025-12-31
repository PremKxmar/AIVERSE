"""
AI Career Companion - India Job Scraper Service
Integrated from Teammate's Verve module.
Uses SearXNG + Crawl4AI + Gemini for scraping 40+ India job platforms.
"""
import os
import sys
import asyncio
import json
import re
import logging
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

# Fix for Windows: Ensure ProactorEventLoop is used for Playwright
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# --- SITE CONFIGURATIONS ---
# Curated list of trusted sources for each category (India focused)

SITE_CONFIGS = {
    "JOB": {
        "sites": [
            "linkedin.com/jobs",
            "indeed.co.in",
            "glassdoor.co.in", 
            "naukri.com",
            "shine.com",
            "foundit.in",
            "freshersworld.com",
            "timesjobs.com",
            "apna.co",
        ],
        "location_filter": "India",
        "results_per_site": 5
    },
    "INTERNSHIP": {
        "sites": [
            "internshala.com",
            "letsintern.com",
            "linkedin.com/jobs",
            "indeed.co.in",
            "glassdoor.co.in",
            "naukri.com",
            "freshersworld.com",
            "unstop.com",
            "stipend.com",
            "twentynineteen.com",
        ],
        "location_filter": "India",
        "results_per_site": 5
    },
    "HACKATHON": {
        "sites": [
            "unstop.com",
            "devpost.com",
            "hack2skill.com",
            "hackerearth.com",
            "devfolio.co",
            "mlh.io",
            "dare2compete.com",
            "techgig.com",
        ],
        "location_filter": "India",
        "results_per_site": 5
    },
    "COURSE": {
        "sites": [
            "youtube.com",
            "coursera.org",
            "udemy.com",
            "freecodecamp.org",
            "edx.org",
            "khanacademy.org",
            "nptel.ac.in",
            "swayam.gov.in",
            "skillshare.com",
            "codecademy.com",
            "geeksforgeeks.org",
            "w3schools.com",
            "tutorialspoint.com",
        ],
        "location_filter": None,
        "results_per_site": 4
    }
}


class SearchResult(BaseModel):
    """Individual search result."""
    url: str
    title: str
    snippet: str
    source: str


class ScraperConfig(BaseModel):
    """Configuration for the scraper."""
    searxng_url: str = "http://localhost:8085"
    searxng_timeout: int = 10
    max_scrape_urls: int = 12
    batch_size: int = 5


class IndiaJobScraper:
    """
    India Job Scraper Service.
    Uses SearXNG for searching and Crawl4AI for scraping.
    """
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig(
            searxng_url=settings.SEARXNG_URL
        )
        self.llm = None  # Will be set when needed
        logger.info(f"🔍 India Job Scraper initialized (SearXNG: {self.config.searxng_url})")
    
    async def search(
        self,
        query: str,
        category: Literal["JOB", "INTERNSHIP", "HACKATHON", "COURSE"]
    ) -> Dict[str, Any]:
        """
        Main search method - orchestrates the full workflow.
        
        Args:
            query: User search query
            category: Type of opportunity to search
            
        Returns:
            Search results with metadata
        """
        logger.info(f"🎯 Starting search: {query} ({category})")
        
        # Step 1: Generate search queries
        search_queries = self._generate_search_queries(query, category)
        logger.info(f"📝 Generated {len(search_queries)} search queries")
        
        # Step 2: Execute SearXNG search
        search_results = await self._execute_searxng_search(search_queries, category)
        logger.info(f"🔗 Found {len(search_results)} URLs")
        
        # Step 3: Scrape URLs (if Crawl4AI available)
        scraped_content = []
        if search_results:
            try:
                scraped_content = await self._scrape_urls(
                    [r["url"] for r in search_results[:self.config.max_scrape_urls]]
                )
                logger.info(f"📖 Scraped {len(scraped_content)} pages")
            except Exception as e:
                logger.warning(f"Scraping failed (Playwright not installed?): {e}")
        
        # Step 4: Extract structured data (if content available)
        extracted_data = []
        if scraped_content:
            try:
                extracted_data = await self._extract_structured_data(
                    scraped_content, category
                )
                logger.info(f"✅ Extracted {len(extracted_data)} listings")
            except Exception as e:
                logger.warning(f"Extraction failed: {e}")
        
        # If no extracted data, return raw search results
        if not extracted_data:
            extracted_data = self._format_search_results(search_results, category)
        
        return {
            "success": True,
            "query": query,
            "category": category,
            "total_results": len(extracted_data),
            "sources": SITE_CONFIGS[category]["sites"],
            "data": extracted_data,
            "metadata": {
                "search_queries_used": len(search_queries),
                "urls_found": len(search_results),
                "pages_scraped": len(scraped_content),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _generate_search_queries(self, query: str, category: str) -> List[str]:
        """Generate search queries for each platform."""
        config = SITE_CONFIGS[category]
        sites = config["sites"]
        location = config.get("location_filter", "India")
        
        queries = []
        
        # Generate queries targeting specific sites
        for site in sites[:5]:  # Top 5 sites
            if category == "JOB":
                queries.append(f'{site} {query} jobs {location} 2024')
                queries.append(f'site:{site} "{query}" vacancy apply')
            elif category == "INTERNSHIP":
                queries.append(f'{site} {query} internship {location}')
                queries.append(f'site:{site} "{query}" intern apply stipend')
            elif category == "HACKATHON":
                queries.append(f'{site} {query} hackathon registration 2025')
            elif category == "COURSE":
                queries.append(f'{site} {query} course free tutorial')
        
        # Add general queries
        queries.append(f'{query} {category.lower()} {location} 2024')
        queries.append(f'"{query}" {location} apply now')
        
        return queries[:15]  # Limit to 15 queries
    
    async def _execute_searxng_search(
        self,
        queries: List[str],
        category: str
    ) -> List[Dict[str, Any]]:
        """Execute searches using SearXNG."""
        all_results = []
        
        async with httpx.AsyncClient(timeout=self.config.searxng_timeout) as client:
            for query in queries:
                try:
                    response = await client.get(
                        f"{self.config.searxng_url}/search",
                        params={
                            "q": query,
                            "format": "json",
                            "language": "en",
                            "pageno": 1
                        }
                    )
                    
                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        
                        for r in results:
                            url = r.get("url", "")
                            
                            # Filter out irrelevant URLs
                            if self._is_relevant_url(url, category):
                                all_results.append({
                                    "url": url,
                                    "title": r.get("title", ""),
                                    "snippet": r.get("content", ""),
                                    "source": r.get("engine", "")
                                })
                                
                except httpx.ConnectError:
                    logger.warning("SearXNG not running. Start with: docker-compose up -d")
                    break
                except Exception as e:
                    logger.warning(f"Search error: {e}")
                    continue
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_results.append(r)
        
        return unique_results
    
    def _is_relevant_url(self, url: str, category: str) -> bool:
        """Check if URL is relevant (not login/about pages)."""
        url_lower = url.lower()
        
        # Skip generic pages
        skip_keywords = [
            'login', 'signup', 'signin', 'register', 'auth',
            'account', 'privacy', 'terms', 'cookie', 'policy',
            'about-us', 'contact', 'faq', 'help', 'support',
            'wikipedia.org', 'reddit.com', 'play.google.com'
        ]
        
        if any(kw in url_lower for kw in skip_keywords):
            return False
        
        # Category-specific filters
        if category == "JOB":
            indicators = ['/jobs/', '/job/', '/careers/', '/vacancy/', '/opening/']
            return any(ind in url_lower for ind in indicators) or \
                   any(site in url_lower for site in ['naukri', 'indeed', 'linkedin', 'glassdoor'])
        
        elif category == "INTERNSHIP":
            indicators = ['/internship', '/intern/', '/jobs/', '/job/']
            return any(ind in url_lower for ind in indicators) or \
                   any(site in url_lower for site in ['internshala', 'letsintern', 'unstop'])
        
        elif category == "HACKATHON":
            indicators = ['/hackathon', '/competition', '/challenge', '/event/']
            return any(ind in url_lower for ind in indicators) or \
                   any(site in url_lower for site in ['unstop', 'devpost', 'devfolio', 'hackerearth'])
        
        elif category == "COURSE":
            indicators = ['/course', '/learn/', '/tutorial', '/class/']
            return any(ind in url_lower for ind in indicators)
        
        return True
    
    async def _scrape_urls(self, urls: List[str]) -> List[str]:
        """Scrape URLs using Crawl4AI."""
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError:
            logger.warning("Crawl4AI not installed. Run: pip install crawl4ai && playwright install")
            return []
        
        scraped = []
        
        async with AsyncWebCrawler(verbose=False, headless=True) as crawler:
            # Process in batches
            for i in range(0, len(urls), self.config.batch_size):
                batch = urls[i:i + self.config.batch_size]
                
                tasks = [self._scrape_single(crawler, url) for url in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, str) and result:
                        scraped.append(result)
        
        return scraped
    
    async def _scrape_single(self, crawler, url: str) -> Optional[str]:
        """Scrape a single URL."""
        try:
            result = await crawler.arun(
                url=url,
                word_count_threshold=30,
                exclude_external_links=True
            )
            
            if result.success and result.markdown:
                content = result.markdown
                # Clean and truncate
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = content[:6000]
                return f"Source: {url}\n\n{content}"
        except Exception as e:
            logger.debug(f"Scrape error for {url}: {e}")
        
        return None
    
    async def _extract_structured_data(
        self,
        content: List[str],
        category: str
    ) -> List[Dict[str, Any]]:
        """Extract structured data using LLM."""
        from app.services.llm_service import get_llm_service
        
        llm = get_llm_service()
        
        # Get schema for category
        schema = self._get_extraction_schema(category)
        
        combined_content = "\n\n---\n\n".join(content[:5])  # Limit for token size
        
        prompt = f"""
Extract ALL {category.lower()} listings from this content.

Return ONLY a JSON array matching this schema:
{schema}

Content:
{combined_content[:50000]}

Output JSON array only:
"""
        
        try:
            result = await llm.generate_json(prompt, "Array of listings")
            if isinstance(result, list):
                return result
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}")
        
        return []
    
    def _get_extraction_schema(self, category: str) -> str:
        """Get JSON schema for category."""
        if category == "JOB":
            return '''[{"role": "string", "company": "string", "location": "string", "experience": "string", "salary": "string", "skills_required": ["string"], "apply_link": "string", "source": "string"}]'''
        elif category == "INTERNSHIP":
            return '''[{"role": "string", "company": "string", "location": "string", "duration": "string", "stipend": "string", "skills_required": ["string"], "apply_link": "string", "source": "string"}]'''
        elif category == "HACKATHON":
            return '''[{"event_name": "string", "organizer": "string", "dates": "string", "prizes": "string", "registration_link": "string", "source": "string"}]'''
        elif category == "COURSE":
            return '''[{"title": "string", "platform": "string", "instructor": "string", "is_free": boolean, "duration": "string", "link": "string"}]'''
        return "[]"
    
    def _format_search_results(
        self,
        results: List[Dict[str, Any]],
        category: str
    ) -> List[Dict[str, Any]]:
        """Format raw search results as structured data."""
        formatted = []
        
        for r in results[:20]:
            if category == "JOB":
                formatted.append({
                    "role": r.get("title", ""),
                    "company": "See listing",
                    "location": "India",
                    "apply_link": r.get("url", ""),
                    "source": self._extract_domain(r.get("url", ""))
                })
            elif category == "INTERNSHIP":
                formatted.append({
                    "role": r.get("title", ""),
                    "company": "See listing",
                    "location": "India",
                    "apply_link": r.get("url", ""),
                    "source": self._extract_domain(r.get("url", ""))
                })
            elif category == "HACKATHON":
                formatted.append({
                    "event_name": r.get("title", ""),
                    "registration_link": r.get("url", ""),
                    "source": self._extract_domain(r.get("url", ""))
                })
            elif category == "COURSE":
                formatted.append({
                    "title": r.get("title", ""),
                    "platform": self._extract_domain(r.get("url", "")),
                    "link": r.get("url", "")
                })
        
        return formatted
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parts = url.split("/")
            if len(parts) > 2:
                return parts[2].replace("www.", "")
        except:
            pass
        return "unknown"


# Singleton instance
_scraper: Optional[IndiaJobScraper] = None

def get_job_scraper() -> IndiaJobScraper:
    """Get or create job scraper instance."""
    global _scraper
    if _scraper is None:
        _scraper = IndiaJobScraper()
    return _scraper
