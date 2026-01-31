"""
RAG Query MCP Server

LightRAG 知识库查询服务 (Port 8002)

工具列表:
- rag_query_data: 从知识库检索 API 接口信息和相关文档
- parse_document_from_url: 解析 URL 文档
"""

from .server import mcp, main

__all__ = ["mcp", "main"]

