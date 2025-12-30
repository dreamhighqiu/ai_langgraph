"""
Azure OpenAI compatibility layer.

This module provides backward compatibility by re-exporting Azure OpenAI functions
from the main openai module where the actual implementation resides.

All core logic for both OpenAI and Azure OpenAI now lives in lightrag.llm.openai,
with this module serving as a thin compatibility wrapper for existing code that
imports from lightrag.llm.azure_openai.
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1VrNWJnPT06NTRiODhiZGQ=

from lightrag.llm.openai import (
    azure_openai_complete_if_cache,
    azure_openai_complete,
    azure_openai_embed,
)
# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1VrNWJnPT06NTRiODhiZGQ=

__all__ = [
    "azure_openai_complete_if_cache",
    "azure_openai_complete",
    "azure_openai_embed",
]
