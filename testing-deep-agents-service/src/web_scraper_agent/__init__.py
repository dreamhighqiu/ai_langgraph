"""Web Scraper Agent - 网站API文档抓取与入库智能体.

提供从网站抓取API文档并存入知识库的功能。
"""

from web_scraper_agent.agent import agent
from web_scraper_agent.tools import (
    web_scraper_tools,
    scrape_api_documentation,
    store_documents_to_knowledge_base,
)

__all__ = [
    "agent",
    "web_scraper_tools",
    "scrape_api_documentation",
    "store_documents_to_knowledge_base",
]
