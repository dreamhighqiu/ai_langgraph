"""服务管理智能体 - 管理统一服务的增删改查.

功能：
1. 知识库管理 - 查询、上传、删除文档
2. Milvus 管理 - 创建/删除集合、向量搜索
3. MinIO 管理 - 上传/下载/删除文件
4. 服务健康检查
"""

import os
import json
import logging
from typing import Annotated, Literal, Optional, List, Any
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from core.llms import deepseek_model
logger = logging.getLogger(__name__)


# =============================================================================
# 扩展的服务管理工具
# =============================================================================

class CreateKnowledgeBaseInput(BaseModel):
    """创建知识库输入."""
    name: str = Field(..., description="知识库名称")
    description: str = Field("", description="描述")


@tool(args_schema=CreateKnowledgeBaseInput)
async def create_knowledge_base(name: str, description: str = "") -> str:
    """创建新的知识库.
    
    用于存储和检索文档，支持智能问答。
    """
    try:
        # 目前 LightRAG 是单知识库模式，返回提示信息
        return json.dumps({
            "success": True,
            "message": f"知识库 '{name}' 配置已记录。当前使用默认知识库。",
            "note": "LightRAG 默认使用 rag_storage 目录作为知识库。",
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"创建知识库失败: {str(e)}"


class DeleteCollectionInput(BaseModel):
    """删除集合输入."""
    name: str = Field(..., description="集合名称")


@tool(args_schema=DeleteCollectionInput)
def delete_milvus_collection(name: str) -> str:
    """删除 Milvus 向量数据库集合.
    
    警告：此操作不可逆，将删除集合中的所有数据。
    """
    try:
        from unified_services.milvus_service import MilvusService
        
        service = MilvusService.get_instance()
        service.drop_collection(name)
        
        return f"集合 '{name}' 已成功删除"
    except Exception as e:
        logger.error(f"Delete collection failed: {e}")
        return f"删除集合失败: {str(e)}"


class CreateBucketInput(BaseModel):
    """创建存储桶输入."""
    name: str = Field(..., description="存储桶名称")


@tool(args_schema=CreateBucketInput)
def create_minio_bucket(name: str) -> str:
    """创建新的 MinIO 存储桶.
    
    用于存储文件和对象。
    """
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        bucket = service.create_bucket(name)
        
        return f"存储桶 '{name}' 创建成功"
    except Exception as e:
        logger.error(f"Create bucket failed: {e}")
        return f"创建存储桶失败: {str(e)}"


class DeleteBucketInput(BaseModel):
    """删除存储桶输入."""
    name: str = Field(..., description="存储桶名称")
    force: bool = Field(False, description="是否强制删除（包括所有文件）")


@tool(args_schema=DeleteBucketInput)
def delete_minio_bucket(name: str, force: bool = False) -> str:
    """删除 MinIO 存储桶.
    
    如果存储桶不为空，需要设置 force=True 强制删除。
    """
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        service.delete_bucket(name, force=force)
        
        return f"存储桶 '{name}' 已成功删除"
    except Exception as e:
        logger.error(f"Delete bucket failed: {e}")
        return f"删除存储桶失败: {str(e)}"


class DeleteFileInput(BaseModel):
    """删除文件输入."""
    bucket_name: str = Field(..., description="存储桶名称")
    object_name: str = Field(..., description="文件名称")


@tool(args_schema=DeleteFileInput)
def delete_file_from_bucket(bucket_name: str, object_name: str) -> str:
    """从 MinIO 存储桶中删除文件."""
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        service.delete_object(object_name, bucket_name)
        
        return f"文件 '{object_name}' 已从 '{bucket_name}' 删除"
    except Exception as e:
        logger.error(f"Delete file failed: {e}")
        return f"删除文件失败: {str(e)}"


class GetBucketStatsInput(BaseModel):
    """获取存储桶统计输入."""
    bucket_name: str = Field(..., description="存储桶名称")


@tool(args_schema=GetBucketStatsInput)
def get_bucket_stats(bucket_name: str) -> str:
    """获取 MinIO 存储桶的统计信息.
    
    返回文件数量、总大小等信息。
    """
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        stats = service.get_bucket_stats(bucket_name)
        
        return json.dumps(stats, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Get bucket stats failed: {e}")
        return f"获取存储桶统计失败: {str(e)}"


class GetCollectionInfoInput(BaseModel):
    """获取集合信息输入."""
    collection_name: str = Field(..., description="集合名称")


@tool(args_schema=GetCollectionInfoInput)
def get_collection_info(collection_name: str) -> str:
    """获取 Milvus 集合的详细信息.
    
    返回向量数量、维度等信息。
    """
    try:
        from unified_services.milvus_service import MilvusService
        
        service = MilvusService.get_instance()
        info = service.get_collection_info(collection_name)
        
        return json.dumps({
            "name": info.name,
            "description": info.description,
            "num_entities": info.num_entities,
            "dimension": info.dimension,
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Get collection info failed: {e}")
        return f"获取集合信息失败: {str(e)}"


@tool
async def check_all_services_health() -> str:
    """检查所有服务的健康状态.
    
    返回 Milvus、MinIO、知识库、数据库的健康状态。
    """
    try:
        from unified_services.milvus_service import MilvusService
        from unified_services.minio_service import MinIOService
        from unified_services.knowledge_service import KnowledgeService
        from unified_services.database_service import DatabaseService
        
        results = {}
        
        # Milvus
        try:
            milvus = MilvusService.get_instance()
            results["milvus"] = milvus.health_check()
        except Exception as e:
            results["milvus"] = {"status": "unhealthy", "error": str(e)}
        
        # MinIO
        try:
            minio = MinIOService.get_instance()
            results["minio"] = minio.health_check()
        except Exception as e:
            results["minio"] = {"status": "unhealthy", "error": str(e)}
        
        # Knowledge
        try:
            knowledge = KnowledgeService.get_instance()
            results["knowledge"] = await knowledge.health_check()
        except Exception as e:
            results["knowledge"] = {"status": "unhealthy", "error": str(e)}
        
        # Database
        try:
            database = DatabaseService.get_instance()
            results["database"] = await database.health_check()
        except Exception as e:
            results["database"] = {"status": "unhealthy", "error": str(e)}
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"健康检查失败: {str(e)}"


# =============================================================================
# 导入基础工具
# =============================================================================

from unified_services.tools import (
    query_knowledge_base,
    query_knowledge_data,
    list_knowledge_bases,
    list_milvus_collections,
    create_milvus_collection,
    search_vectors,
    list_minio_buckets,
    list_files_in_bucket,
    get_file_download_url,
)

# 所有工具列表
tools = [
    # 知识库管理
    query_knowledge_base,
    query_knowledge_data,
    list_knowledge_bases,
    create_knowledge_base,
    # Milvus 管理
    list_milvus_collections,
    create_milvus_collection,
    delete_milvus_collection,
    get_collection_info,
    search_vectors,
    # MinIO 管理
    list_minio_buckets,
    create_minio_bucket,
    delete_minio_bucket,
    list_files_in_bucket,
    delete_file_from_bucket,
    get_bucket_stats,
    get_file_download_url,
    # 健康检查
    check_all_services_health,
]


# =============================================================================
# 状态定义
# =============================================================================

class State(BaseModel):
    """智能体状态."""
    messages: Annotated[list, add_messages]


# =============================================================================
# 智能体节点
# =============================================================================


# 系统提示
SYSTEM_PROMPT = """你是一个专业的服务管理智能体，负责管理和操作统一服务层。

你可以帮助用户完成以下任务：

## 知识库管理
- 查询知识库内容（支持多种查询模式：naive, local, global, hybrid, mix）
- 列出所有知识库
- 查询知识图谱数据（实体、关系、文档块）

## Milvus 向量数据库管理
- 列出所有集合（Collections）
- 创建新集合（指定名称、维度）
- 删除集合
- 获取集合详细信息
- 向量相似度搜索

## MinIO 对象存储管理
- 列出所有存储桶（Buckets）
- 创建新存储桶
- 删除存储桶
- 列出存储桶中的文件
- 删除文件
- 获取文件下载链接
- 查看存储桶统计信息

## 服务健康检查
- 检查所有服务的健康状态

使用工具时请注意：
1. 删除操作不可逆，请先确认用户意图
2. 对于敏感操作，先告知用户可能的影响
3. 如果操作失败，提供清晰的错误信息和建议

回答时使用中文，保持专业和友好。"""


def agent_node(state: State):
    """智能体推理节点."""
    llm = deepseek_model
    llm_with_tools = llm.bind_tools(tools)
    
    # 添加系统提示
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state.messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: State) -> Literal["tools", END]:
    """判断是否需要继续调用工具."""
    last_message = state.messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# =============================================================================
# 构建图
# =============================================================================

def build_graph():
    """构建智能体图."""
    graph = StateGraph(State)
    
    # 添加节点
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    
    # 添加边
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, ["tools", END])
    graph.add_edge("tools", "agent")
    
    return graph.compile()


# 导出智能体
agent = build_graph()

