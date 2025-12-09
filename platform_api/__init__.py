"""
Platform API package consolidating FastAPI gateway logic for DeepAgent, RAG, and MCP services.
"""

from .main import app, create_app

__all__ = ["app", "create_app"]
