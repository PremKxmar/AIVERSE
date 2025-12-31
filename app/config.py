"""
AI Career Companion - Configuration Settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "AI Career Companion"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Google Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    
    # Supabase (added)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Database
    POSTGRES_URL: str = "postgresql://localhost:5432/career_companion"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Store
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Job Scraper
    SEARXNG_URL: str = "http://localhost:8080"
    SCRAPING_BATCH_SIZE: int = 5
    MAX_SCRAPE_URLS: int = 12
    
    # LLM Settings
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore unknown env vars


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
