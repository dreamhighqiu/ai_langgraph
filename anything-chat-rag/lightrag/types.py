

from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Optional

# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmxJNE13PT06Yjg3OTEwMTQ=

class GPTKeywordExtractionFormat(BaseModel):
    high_level_keywords: list[str]
    low_level_keywords: list[str]


class KnowledgeGraphNode(BaseModel):
    id: str
    labels: list[str]
    properties: dict[str, Any]  # anything else goes here
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmxJNE13PT06Yjg3OTEwMTQ=


class KnowledgeGraphEdge(BaseModel):
    id: str
    type: Optional[str]
    source: str  # id of source node
    target: str  # id of target node
    properties: dict[str, Any]  # anything else goes here


class KnowledgeGraph(BaseModel):
    nodes: list[KnowledgeGraphNode] = []
    edges: list[KnowledgeGraphEdge] = []
    is_truncated: bool = False
