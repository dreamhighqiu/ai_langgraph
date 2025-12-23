"""
RAG Anything MCP Server

A professional MCP server implementation for RAG Anything framework,
providing comprehensive document processing and multimodal querying capabilities.

Features:
- Multi-format document processing (PDF, Office, Images, etc.)
- Multimodal content handling (images, tables, equations)
- Hybrid retrieval with knowledge graphs
- VLM-enhanced querying
- Batch processing support
- Knowledge base management

Usage:
    python -m mcp_server_rag_anything.server

Configuration:
    Set environment variables in .env file:
    - LLM_API_KEY: Your LLM API key
    - LLM_MODEL: LLM model name
    - EMBEDDING_MODEL: Embedding model
    - RAG_WORKING_DIR: Working directory for RAG storage
    - RAG_PARSER: Parser type (docling or mineru)
"""



__version__ = "0.1.0"
__author__ = "RAG Anything MCP Team"
__all__ = [
    "RAGAnythingConnector",
    "MCSConfig",
    "server",
]
# type: ignore  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0dseVdnPT06YjU1NjBjNzM=

from .config import MCSConfig
from .connector import RAGAnythingConnector
from . import server

# noqa  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0dseVdnPT06YjU1NjBjNzM=
