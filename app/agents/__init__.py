"""
AI Career Companion - Agents Package
All 7 Agentic Modules.
"""
from .base import BaseAgent
from .digital_twin import DigitalTwinAgent
from .market_oracle import MarketOracleAgent
from .roadmap_architect import RoadmapArchitectAgent
from .action_agent import ActionAgent
from .evolution_loop import EvolutionLoopAgent
from .go_beyond import GoBeyondAgent
from .orchestrator import OrchestratorAgent

__all__ = [
    "BaseAgent",
    "DigitalTwinAgent",      # Module 1
    "MarketOracleAgent",     # Module 2
    "RoadmapArchitectAgent", # Module 3
    "ActionAgent",           # Module 4
    "EvolutionLoopAgent",    # Module 5
    "GoBeyondAgent",         # Module 6
    "OrchestratorAgent",     # Module 7
]
