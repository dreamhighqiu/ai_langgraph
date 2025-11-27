"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from langchain_core.tools import tool

import asyncio
import json
import os
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import tool
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVc5UmJ3PT06ZmIwYjRmNTY=

@tool
def get_available_collections() -> str:
    """
    获取所有可用的集合信息。
    返回所有可用的集合名称和描述，帮助选择合适的集合来查询知识。

    Returns:
        str: 包含所有集合信息的JSON字符串，每个集合包含name和description字段
    """
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    collections_file = current_dir / "collections.json"
# noqa  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVc5UmJ3PT06ZmIwYjRmNTY=

    try:
        with open(collections_file, 'r', encoding='utf-8') as f:
            collections = json.load(f)
        return json.dumps(collections, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        return json.dumps({"error": "collections.json文件不存在"}, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({"error": "collections.json文件格式错误"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"读取集合信息失败: {str(e)}"}, ensure_ascii=False)

def get_mcp_rag_tools():
    client = MultiServerMCPClient(
                {
                    "mcp-server-rag": {
                        "url": "http://127.0.0.1:8001/sse",
                        "transport": "sse",
                    }
                }
            )
    tools = asyncio.run(client.get_tools())
    return tools

# print(get_mcp_rag_tools())