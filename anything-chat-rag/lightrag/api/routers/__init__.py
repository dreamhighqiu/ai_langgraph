"""
This module contains all the routers for the LightRAG API.
"""


# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U1hCcFNBPT06YmUxYTAyNjA=

from .document_routes import router as document_router
from .query_routes import router as query_router
from .graph_routes import router as graph_router
from .ollama_api import OllamaAPI

__all__ = ["document_router", "query_router", "graph_router", "OllamaAPI"]
# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U1hCcFNBPT06YmUxYTAyNjA=
