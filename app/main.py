"""
AI Career Companion - FastAPI Application
Main entry point for the API.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.config import settings
from app.agents.orchestrator import OrchestratorAgent
from app.routers import onboard, jobs, career, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Optional[OrchestratorAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global orchestrator
    
    # Startup
    logger.info("🚀 Starting AI Career Companion...")
    orchestrator = OrchestratorAgent()
    logger.info("✅ All agents initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down AI Career Companion...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI Career Development Assistant - 7 Module Architecture",
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(onboard.router, prefix="/api/v1", tags=["Onboarding"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs & Market"])
app.include_router(career.router, prefix="/api/v1", tags=["Career Development"])


# ============== Request/Response Models ==============

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = "default"


class ActionRequest(BaseModel):
    """Generic action request."""
    action: str
    session_id: Optional[str] = "default"
    data: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    agents_ready: bool


# ============== Core Endpoints ==============

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.API_VERSION,
        agents_ready=orchestrator is not None
    )


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "debug": settings.DEBUG,
        "orchestrator": orchestrator is not None
    }


@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Routes messages through the orchestrator.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    result = await orchestrator.process({
        "session_id": request.session_id,
        "message": request.message,
        "action": "chat"
    })
    
    return result


@app.post("/api/v1/action")
async def perform_action(request: ActionRequest):
    """
    Generic action endpoint.
    Routes actions through the orchestrator.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    result = await orchestrator.process({
        "session_id": request.session_id,
        "action": request.action,
        **request.data
    })
    
    return result


@app.get("/api/v1/session/{session_id}")
async def get_session(session_id: str):
    """Get session state for debugging."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    state = orchestrator.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return state


@app.get("/api/v1/session/{session_id}/reasoning")
async def get_reasoning_trace(session_id: str):
    """Get reasoning trace for transparency."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    trace = orchestrator.get_reasoning_trace(session_id)
    return {"session_id": session_id, "reasoning_trace": trace}


# ============== Utility function for routers ==============

def get_orchestrator() -> OrchestratorAgent:
    """Get the global orchestrator instance."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    return orchestrator


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
