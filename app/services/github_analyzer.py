"""
AI Career Companion - GitHub Analyzer Service
Analyzes GitHub profiles and repositories.
"""
import logging
from typing import Optional, Dict, Any, List
from github import Github
from app.config import settings

logger = logging.getLogger(__name__)


class GitHubAnalyzerService:
    """
    GitHub analysis service.
    Extracts skills, projects, and activity from GitHub profiles.
    """
    
    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN) if settings.GITHUB_TOKEN else None
        if self.github:
            logger.info("🐙 GitHub Analyzer initialized with token")
        else:
            logger.warning("⚠️ GitHub Analyzer initialized without token (limited API)")
            self.github = Github()  # Anonymous access
    
    async def analyze_user(self, username: str) -> Dict[str, Any]:
        """
        Analyze a GitHub user profile.
        
        Args:
            username: GitHub username
            
        Returns:
            Analysis results
        """
        try:
            user = self.github.get_user(username)
            
            analysis = {
                "username": username,
                "name": user.name,
                "bio": user.bio,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "profile_url": user.html_url,
                "repositories": [],
                "languages": {},
                "skills_detected": [],
                "activity_score": 0
            }
            
            # Analyze repositories
            repos = list(user.get_repos())[:20]  # Limit to 20 repos
            
            language_counts = {}
            total_stars = 0
            total_commits = 0
            
            for repo in repos:
                if not repo.fork:  # Skip forked repos
                    repo_info = {
                        "name": repo.name,
                        "description": repo.description,
                        "url": repo.html_url,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "language": repo.language,
                        "topics": repo.get_topics() if hasattr(repo, 'get_topics') else [],
                        "has_readme": False
                    }
                    
                    # Check for README
                    try:
                        repo.get_contents("README.md")
                        repo_info["has_readme"] = True
                    except:
                        pass
                    
                    analysis["repositories"].append(repo_info)
                    
                    # Count languages
                    if repo.language:
                        language_counts[repo.language] = language_counts.get(repo.language, 0) + 1
                    
                    total_stars += repo.stargazers_count
            
            # Sort languages by frequency
            analysis["languages"] = dict(
                sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
            )
            
            # Detect skills from languages and topics
            skills = list(language_counts.keys())
            analysis["skills_detected"] = skills
            
            # Calculate activity score (simple heuristic)
            analysis["activity_score"] = min(100, (
                (user.public_repos * 2) +
                (total_stars * 5) +
                (user.followers) +
                (len([r for r in analysis["repositories"] if r["has_readme"]]) * 10)
            ))
            
            logger.info(f"Analyzed GitHub user: {username} ({len(repos)} repos)")
            return analysis
            
        except Exception as e:
            logger.error(f"GitHub analysis error for {username}: {e}")
            return {
                "username": username,
                "error": str(e),
                "repositories": [],
                "languages": {},
                "skills_detected": []
            }
    
    async def analyze_repo(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Deep analyze a specific repository.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Detailed repo analysis
        """
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Get language breakdown
            languages = repo.get_languages()
            total_bytes = sum(languages.values())
            language_percentages = {
                lang: round((bytes_count / total_bytes) * 100, 1)
                for lang, bytes_count in languages.items()
            }
            
            # Get README content
            readme_content = None
            try:
                readme = repo.get_contents("README.md")
                readme_content = readme.decoded_content.decode()[:2000]  # First 2000 chars
            except:
                pass
            
            analysis = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "watchers": repo.watchers_count,
                "language_breakdown": language_percentages,
                "topics": repo.get_topics() if hasattr(repo, 'get_topics') else [],
                "readme_preview": readme_content,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "has_wiki": repo.has_wiki,
                "has_issues": repo.has_issues,
                "open_issues": repo.open_issues_count,
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Repo analysis error for {owner}/{repo_name}: {e}")
            return {"error": str(e)}
    
    def detect_technologies(self, repo_analysis: Dict[str, Any]) -> List[str]:
        """
        Detect specific technologies/frameworks from repo analysis.
        """
        technologies = []
        
        # From languages
        technologies.extend(repo_analysis.get("languages", {}).keys())
        
        # From topics
        technologies.extend(repo_analysis.get("topics", []))
        
        # From README content (simple keyword detection)
        readme = repo_analysis.get("readme_preview", "") or ""
        readme_lower = readme.lower()
        
        tech_keywords = [
            "react", "vue", "angular", "django", "flask", "fastapi",
            "tensorflow", "pytorch", "keras", "scikit-learn",
            "docker", "kubernetes", "aws", "gcp", "azure",
            "mongodb", "postgresql", "mysql", "redis",
            "node", "express", "nextjs", "tailwind"
        ]
        
        for tech in tech_keywords:
            if tech in readme_lower and tech not in [t.lower() for t in technologies]:
                technologies.append(tech.title())
        
        return list(set(technologies))


# Singleton instance
_github_service: Optional[GitHubAnalyzerService] = None

def get_github_analyzer() -> GitHubAnalyzerService:
    """Get or create GitHub analyzer service."""
    global _github_service
    if _github_service is None:
        _github_service = GitHubAnalyzerService()
    return _github_service
