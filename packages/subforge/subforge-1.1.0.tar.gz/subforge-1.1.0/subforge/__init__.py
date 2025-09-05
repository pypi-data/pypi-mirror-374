"""
SubForge - Forge your perfect Claude Code development team
"""

__version__ = "1.1.0"
__author__ = "SubForge Contributors"
__description__ = "AI-powered subagent factory for Claude Code developers"
__license__ = "MIT"

# Core imports for easier access
from .core.project_analyzer import ProjectAnalyzer
from .core.validation_engine import ValidationEngine
from .core.workflow_orchestrator import WorkflowOrchestrator

__all__ = [
    "ProjectAnalyzer",
    "WorkflowOrchestrator",
    "ValidationEngine",
    "__version__",
    "__author__",
    "__description__",
    "__license__",
]