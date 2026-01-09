"""
测试用例生成智能体工具集

提供测试用例创建和更新的工具函数，供智能体调用
通过 HTTP 接口调用，降低耦合度
"""



from typing import Optional, Any
import logging
import os
import httpx

from app.config.settings import settings
from app.agents.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

# 初始化 PDF 处理器（全局单例，启用缓存）
_pdf_processor = PDFProcessor(enable_cache=True)


# ============ 配置 ============

# API 基础 URL（从环境变量读取，默认使用 8080 端口）
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8080")
API_PREFIX = settings.api_prefix  # /api/v2

# HTTP 请求超时时间（从环境变量读取）
HTTP_TIMEOUT = float(os.environ.get("HTTP_TIMEOUT", "30.0"))
# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVZSMldRPT06MTk4YTZlNjI=


# ============ 辅助函数 ============

def get_api_url(path: str) -> str:
    """构建完整的 API URL"""
    return f"{API_BASE_URL}{API_PREFIX}{path}"


async def make_http_request(
    method: str,
    url: str,
    json_data: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: Optional[float] = None,
) -> dict[str, Any]:
    """
    发送 HTTP 请求的通用函数

    Args:
        method: HTTP 方法（GET, POST, PATCH, DELETE）
        url: 完整的 URL
        json_data: JSON 请求体
        params: URL 查询参数
        timeout: 超时时间（秒），默认使用 HTTP_TIMEOUT

    Returns:
        dict: 响应数据
    
    Raises:
        Exception: 请求失败时抛出异常
    """
    timeout_value = timeout or HTTP_TIMEOUT
    
    try:
        async with httpx.AsyncClient(timeout=timeout_value) as client:
            response = await client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        # HTTP 错误（4xx, 5xx）
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", error_detail)
        except Exception:
            pass
        raise Exception(f"HTTP {e.response.status_code}: {error_detail}")
    except httpx.RequestError as e:
        # 网络错误
        raise Exception(f"网络请求失败: {str(e)}")
    except Exception as e:
        # 其他错误
        raise Exception(f"请求失败: {str(e)}")


# ============ 工具函数 ============

async def create_test_case_tool(
    project_identifier: str,
    folder_id: str,
    name: str,
    description: Optional[str] = None,
    preconditions: Optional[str] = None,
    priority: str = "medium",
    status: str = "draft",
    case_type: str = "functional",
    owner: Optional[str] = None,
    tags: Optional[list[str]] = None,
    issues: Optional[list[str]] = None,
    automation_status: str = "not_automated",
    custom_fields: Optional[dict[str, Any]] = None,
    template: str = "test_case",
    test_case_steps: Optional[list[dict[str, str]]] = None,
    feature: Optional[str] = None,
    scenario: Optional[str] = None,
    background: Optional[str] = None,
) -> dict[str, Any]:
    """
    创建测试用例工具（通过 HTTP 接口调用）

    该工具通过调用测试用例创建 HTTP 接口来创建新的测试用例。
    支持普通测试用例和 BDD 测试用例两种模板。

    Args:
        project_identifier: 项目标识符，如 'PROJ-001'
        folder_id: 文件夹 UUID
        name: 测试用例名称（必填）
        description: 测试用例描述（可选，支持 HTML）
        preconditions: 前置条件（可选，支持 HTML）
        priority: 优先级，可选值：critical, high, medium, low（默认 medium）
        status: 状态，可选值：active, draft, in_review, rejected, outdated（默认 draft）
        case_type: 测试类型，可选值：functional, regression, smoke_sanity, acceptance,
                   performance, security, usability, compatibility, accessibility,
                   destructive, other（默认 functional）
        owner: 负责人邮箱（可选）
        tags: 标签列表（可选）
        issues: 关联的 Jira issues（可选）
        automation_status: 自动化状态，可选值：not_automated, automated, in_progress,
                          obsolete（默认 not_automated）
        custom_fields: 自定义字段（可选）
        template: 模板类型，可选值：test_case（普通）, test_case_bdd（BDD）（默认 test_case）
        test_case_steps: 测试步骤列表（普通测试用例使用），每个步骤包含：
                        - step: 操作步骤描述（必填）
                        - result: 预期结果（可选）
        feature: BDD Feature 描述（BDD 测试用例必填）
        scenario: BDD Scenario 描述（BDD 测试用例必填）
        background: BDD Background 描述（BDD 测试用例可选）

    Returns:
        dict: 包含创建结果的字典
            - success: 是否成功
            - data: 创建的测试用例信息（如果成功）
            - error: 错误信息（如果失败）

    Examples:
        # 创建普通测试用例
        result = await create_test_case_tool(
            project_identifier="PROJ-001",
            folder_id="123e4567-e89b-12d3-a456-426614174000",
            name="用户登录功能测试",
            description="验证用户登录功能是否正常",
            priority="high",
            status="active",
            case_type="functional",
            test_case_steps=[
                {"step": "打开登录页面", "result": "页面正常显示"},
                {"step": "输入用户名和密码", "result": "输入框接受输入"},
                {"step": "点击登录按钮", "result": "成功登录并跳转到首页"}
            ],
            tags=["登录", "核心功能"]
        )

        # 创建 BDD 测试用例
        result = await create_test_case_tool(
            project_identifier="PROJ-001",
            folder_id="123e4567-e89b-12d3-a456-426614174000",
            name="用户登录场景",
            template="test_case_bdd",
            feature="用户认证",
            scenario="用户使用正确的凭据登录",
            background="Given 用户已注册"
        )
    """
    try:
        # 构建请求数据
        request_data: dict[str, Any] = {
            "name": name,
            "template": template,
            "priority": priority,
            "status": status,
            "case_type": case_type,
            "automation_status": automation_status,
        }

        # 添加可选字段
        if description is not None:
            request_data["description"] = description
        if preconditions is not None:
            request_data["preconditions"] = preconditions
        if owner is not None:
            request_data["owner"] = owner
        if tags is not None:
            request_data["tags"] = tags
        if issues is not None:
            request_data["issues"] = issues
        if custom_fields is not None:
            request_data["custom_fields"] = custom_fields

        # 根据模板类型添加相应字段
        if template == "test_case_bdd":
            # BDD 测试用例
            if feature is not None:
                request_data["feature"] = feature
            if scenario is not None:
                request_data["scenario"] = scenario
            if background is not None:
                request_data["background"] = background
        else:
            # 普通测试用例
            if test_case_steps is not None:
                request_data["test_case_steps"] = test_case_steps

        # 构建 API URL（需要包含 project_identifier 路径参数）
        url = get_api_url(f"/projects/{project_identifier}/folders/{folder_id}/test-cases")

        # 不需要查询参数，project_identifier 已经在路径中
        params = None

        # 发送 HTTP POST 请求
        response_data = await make_http_request(
            method="POST",
            url=url,
            json_data=request_data,
            params=params,
        )

        # 提取响应数据
        if response_data.get("success"):
            test_case_data = response_data.get("data", {})
            return {
                "success": True,
                "data": test_case_data,
                "message": f"测试用例 {test_case_data.get('identifier', '')} 创建成功"
            }
        else:
            return {
                "success": False,
                "error": "API 返回失败",
                "message": "创建测试用例失败"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"创建测试用例失败: {str(e)}"
        }
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVZSMldRPT06MTk4YTZlNjI=


async def update_test_case_tool(
    project_identifier: str,
    test_case_identifier: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    preconditions: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    case_type: Optional[str] = None,
    folder_id: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[list[str]] = None,
    issues: Optional[list[str]] = None,
    automation_status: Optional[str] = None,
    custom_fields: Optional[dict[str, Any]] = None,
    test_case_steps: Optional[list[dict[str, str]]] = None,
    feature: Optional[str] = None,
    scenario: Optional[str] = None,
    background: Optional[str] = None,
) -> dict[str, Any]:
    """
    更新测试用例工具（通过 HTTP 接口调用）

    该工具通过调用测试用例更新 HTTP 接口来更新现有测试用例的信息。
    所有字段都是可选的，只更新提供的字段。

    Args:
        project_identifier: 项目标识符，如 'PROJ-001'
        test_case_identifier: 测试用例标识符，如 'TC-1234'
        name: 测试用例名称
        description: 测试用例描述
        preconditions: 前置条件
        priority: 优先级（critical, high, medium, low）
        status: 状态（active, draft, in_review, rejected, outdated）
        case_type: 测试类型
        folder_id: 所属文件夹 UUID（用于移动测试用例）
        owner: 负责人邮箱
        tags: 标签列表
        issues: 关联的 Jira issues
        automation_status: 自动化状态
        custom_fields: 自定义字段
        test_case_steps: 测试步骤列表
        feature: BDD Feature 描述
        scenario: BDD Scenario 描述
        background: BDD Background 描述

    Returns:
        dict: 包含更新结果的字典
            - success: 是否成功
            - data: 更新后的测试用例信息（如果成功）
            - error: 错误信息（如果失败）

    Examples:
        # 更新测试用例的优先级和状态
        result = await update_test_case_tool(
            project_identifier="PROJ-001",
            test_case_identifier="TC-1234",
            priority="critical",
            status="active"
        )

        # 更新测试步骤
        result = await update_test_case_tool(
            project_identifier="PROJ-001",
            test_case_identifier="TC-1234",
            test_case_steps=[
                {"step": "新步骤1", "result": "预期结果1"},
                {"step": "新步骤2", "result": "预期结果2"}
            ]
        )

        # 移动测试用例到另一个文件夹
        result = await update_test_case_tool(
            project_identifier="PROJ-001",
            test_case_identifier="TC-1234",
            folder_id="456e7890-e89b-12d3-a456-426614174000"
        )
    """
    try:
        # 构建更新数据（只包含提供的字段）
        request_data: dict[str, Any] = {}

        if name is not None:
            request_data["name"] = name
        if description is not None:
            request_data["description"] = description
        if preconditions is not None:
            request_data["preconditions"] = preconditions
        if priority is not None:
            request_data["priority"] = priority
        if status is not None:
            request_data["status"] = status
        if case_type is not None:
            request_data["case_type"] = case_type
        if folder_id is not None:
            request_data["folder_id"] = folder_id
        if owner is not None:
            request_data["owner"] = owner
        if tags is not None:
            request_data["tags"] = tags
        if issues is not None:
            request_data["issues"] = issues
        if automation_status is not None:
            request_data["automation_status"] = automation_status
        if custom_fields is not None:
            request_data["custom_fields"] = custom_fields
        if test_case_steps is not None:
            request_data["test_case_steps"] = test_case_steps
        if feature is not None:
            request_data["feature"] = feature
        if scenario is not None:
            request_data["scenario"] = scenario
        if background is not None:
            request_data["background"] = background

        # 如果没有任何字段需要更新，返回错误
        if not request_data:
            return {
                "success": False,
                "error": "没有提供任何需要更新的字段",
                "message": "更新测试用例失败：没有提供任何需要更新的字段"
            }

        # 构建 API URL（需要包含 project_identifier 路径参数）
        url = get_api_url(f"/projects/{project_identifier}/test-cases/{test_case_identifier}")

        # 不需要查询参数，project_identifier 已经在路径中
        params = None

        # 发送 HTTP PATCH 请求
        response_data = await make_http_request(
            method="PATCH",
            url=url,
            json_data=request_data,
            params=params,
        )

        # 提取响应数据
        if response_data.get("success"):
            test_case_data = response_data.get("data", {})
            return {
                "success": True,
                "data": test_case_data,
                "message": f"测试用例 {test_case_data.get('identifier', '')} 更新成功"
            }
        else:
            return {
                "success": False,
                "error": "API 返回失败",
                "message": "更新测试用例失败"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"更新测试用例失败: {str(e)}"
        }


async def batch_create_test_cases_tool(
    project_identifier: str,
    folder_id: str,
    test_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    批量创建测试用例工具（通过 HTTP 接口调用）

    该工具可以一次性创建多个测试用例，提高效率。
    每个测试用例的参数与 create_test_case_tool 相同。

    Args:
        project_identifier: 项目标识符，如 'PROJ-001'
        folder_id: 文件夹 UUID
        test_cases: 测试用例列表，每个元素是一个包含测试用例信息的字典，包含以下字段：
            - name: 测试用例名称（必填）
            - description: 测试用例描述（可选）
            - preconditions: 前置条件（可选）
            - priority: 优先级（可选，默认 medium）
            - status: 状态（可选，默认 draft）
            - case_type: 测试类型（可选，默认 functional）
            - owner: 负责人邮箱（可选）
            - tags: 标签列表（可选）
            - issues: 关联的 Jira issues（可选）
            - automation_status: 自动化状态（可选，默认 not_automated）
            - custom_fields: 自定义字段（可选）
            - template: 模板类型（可选，默认 test_case）
            - test_case_steps: 测试步骤列表（可选）
            - feature: BDD Feature 描述（可选）
            - scenario: BDD Scenario 描述（可选）
            - background: BDD Background 描述（可选）

    Returns:
        dict: 包含批量创建结果的字典
            - success: 是否成功
            - data: 包含成功和失败的统计信息
                - total: 总数
                - succeeded: 成功数量
                - failed: 失败数量
                - results: 每个测试用例的创建结果列表
            - error: 错误信息（如果失败）

    Examples:
        # 批量创建多个测试用例
        result = await batch_create_test_cases_tool(
            project_identifier="PROJ-001",
            folder_id="123e4567-e89b-12d3-a456-426614174000",
            test_cases=[
                {
                    "name": "测试用例1",
                    "description": "描述1",
                    "priority": "high",
                    "test_case_steps": [
                        {"step": "步骤1", "result": "结果1"}
                    ]
                },
                {
                    "name": "测试用例2",
                    "description": "描述2",
                    "priority": "medium",
                    "test_case_steps": [
                        {"step": "步骤1", "result": "结果1"}
                    ]
                },
                {
                    "name": "BDD 测试用例",
                    "template": "test_case_bdd",
                    "feature": "用户登录",
                    "scenario": "成功登录"
                }
            ]
        )
    """
    try:
        if not test_cases:
            return {
                "success": False,
                "error": "测试用例列表为空",
                "message": "批量创建失败：测试用例列表为空"
            }

        results = []
        succeeded = 0
        failed = 0

        # 逐个创建测试用例
        for index, test_case_data in enumerate(test_cases):
            try:
                # 提取测试用例参数
                name = test_case_data.get("name")
                if not name:
                    results.append({
                        "index": index,
                        "success": False,
                        "error": "测试用例名称不能为空",
                        "data": test_case_data
                    })
                    failed += 1
                    continue

                # 调用单个创建工具
                result = await create_test_case_tool(
                    project_identifier=project_identifier,
                    folder_id=folder_id,
                    name=name,
                    description=test_case_data.get("description"),
                    preconditions=test_case_data.get("preconditions"),
                    priority=test_case_data.get("priority", "medium"),
                    status=test_case_data.get("status", "draft"),
                    case_type=test_case_data.get("case_type", "functional"),
                    owner=test_case_data.get("owner"),
                    tags=test_case_data.get("tags"),
                    issues=test_case_data.get("issues"),
                    automation_status=test_case_data.get("automation_status", "not_automated"),
                    custom_fields=test_case_data.get("custom_fields"),
                    template=test_case_data.get("template", "test_case"),
                    test_case_steps=test_case_data.get("test_case_steps"),
                    feature=test_case_data.get("feature"),
                    scenario=test_case_data.get("scenario"),
                    background=test_case_data.get("background"),
                )

                results.append({
                    "index": index,
                    "success": result.get("success", False),
                    "data": result.get("data"),
                    "error": result.get("error"),
                    "message": result.get("message")
                })
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVZSMldRPT06MTk4YTZlNjI=

                if result.get("success"):
                    succeeded += 1
                else:
                    failed += 1

            except Exception as e:
                results.append({
                    "index": index,
                    "success": False,
                    "error": str(e),
                    "data": test_case_data
                })
                failed += 1

        return {
            "success": True,
            "data": {
                "total": len(test_cases),
                "succeeded": succeeded,
                "failed": failed,
                "results": results
            },
            "message": f"批量创建完成：成功 {succeeded} 个，失败 {failed} 个"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"批量创建测试用例失败: {str(e)}"
        }


# ============ RAG 检索工具 ============

async def rag_query_tool(
    query: str,
    mode: str = "mix",
    top_k: int = 10,
    chunk_top_k: int = 5,
    enable_rerank: bool = True,
) -> dict[str, Any]:
    """
    从 RAG 知识库检索相关上下文信息
    
    该工具调用 RAG MCP 服务器，从知识库中检索与查询相关的信息。
    主要用于：
    - 检索 API 接口的详细信息（URL、参数、认证方式等）
    - 查找接口的使用示例和测试数据
    - 获取历史测试记录和基准值
    - 了解接口的依赖关系
    
    Args:
        query: 查询描述（如"获取首页信息接口"、"用户登录API"）
        mode: 检索模式，可选值：
            - mix (推荐): 结合知识图谱和向量检索
            - local: 获取直接相关的实体和关系
            - naive: 仅使用向量相似性搜索
            - global: 探索知识图谱中的全局关系
            - hybrid: 结合本地和全局检索
        top_k: 返回的顶部实体/关系数量（默认10）
        chunk_top_k: 返回的文本块数量（默认5）
        enable_rerank: 是否启用重排序（默认True）
    
    Returns:
        dict: 包含检索结果的字典
            - success: bool, 是否成功
            - context: str, 检索到的上下文信息
            - entities: list, 相关实体列表
            - chunks: list, 相关文本块列表
            - error: str, 错误信息（如果失败）
    
    Examples:
        >>> result = await rag_query_tool("用户登录接口的详细信息")
        >>> if result["success"]:
        >>>     print(result["context"])
    """
    try:
        # RAG MCP 服务器地址（从环境变量读取）
        rag_base_url = os.environ.get("RAG_MCP_URL", "http://localhost:9002")
        
        logger.info(f"开始 RAG 检索: {query} (模式: {mode})")
        
        # 调用 RAG MCP 服务器
        request_body = {
            "query": query,
            "mode": mode,
            "top_k": top_k,
            "chunk_top_k": chunk_top_k,
            "enable_rerank": enable_rerank,
            "include_references": True,
            "include_chunk_content": True,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 调用 RAG 工具
            # 注意：这里假设 RAG MCP 服务器提供了 REST API 端点
            # 实际使用时可能需要通过 MCP 协议调用
            response = await client.post(
                f"{rag_base_url}/rag/query",
                json=request_body
            )
            response.raise_for_status()
            rag_response = response.json()
        
        # 解析 RAG 响应
        if rag_response.get("status") == "success":
            data = rag_response.get("data", {})
            entities = data.get("entities", [])
            chunks = data.get("chunks", [])
            
            # 构建上下文文本
            context_parts = []
            
            # 添加文本块内容
            if chunks:
                context_parts.append("## 相关文档信息")
                for i, chunk in enumerate(chunks[:3], 1):
                    content = chunk.get("content", "")
                    if content:
                        context_parts.append(f"\n### 文档片段 {i}")
                        context_parts.append(content)
            
            # 添加实体信息
            if entities:
                context_parts.append("\n## 相关实体")
                for entity in entities[:5]:
                    name = entity.get("entity_name", "")
                    desc = entity.get("description", "")
                    if name:
                        context_parts.append(f"- **{name}**: {desc}")
            
            context_text = "\n".join(context_parts)
            
            logger.info(f"RAG 检索成功，找到 {len(entities)} 个实体和 {len(chunks)} 个文本块")
            
            return {
                "success": True,
                "context": context_text,
                "entities": entities,
                "chunks": chunks,
                "metadata": rag_response.get("metadata", {}),
            }
        else:
            return {
                "success": False,
                "error": rag_response.get("message", "RAG 检索失败"),
                "context": "",
            }
    
    except httpx.HTTPError as e:
        logger.error(f"RAG 服务请求失败: {e}")
        return {
            "success": False,
            "error": f"RAG 服务请求失败: {str(e)}",
            "context": "",
        }
    except Exception as e:
        logger.error(f"RAG 检索失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"RAG 检索失败: {str(e)}",
            "context": "",
        }


# ============ 文档解析工具 ============

async def parse_document_from_url(
    url: str,
    document_type: Optional[str] = None,
) -> dict[str, Any]:
    """
    从 URL 下载并解析文档内容

    支持的文档类型:
    - PDF: 使用 PyMuPDF4LLM (支持表格) 或 PyPDF2 (备用)
    - 图片: 返回图片信息，需要配合视觉模型使用
    - TXT: 纯文本解析

    Args:
        url: 文档的 URL (通常是 MinIO 预签名 URL)
        document_type: 文档 MIME 类型 (可选，用于优化解析策略)

    Returns:
        dict: 包含解析结果的字典
            - success: bool, 是否成功
            - content: str, 解析的文本内容
            - document_type: str, 文档类型
            - error: str, 错误信息 (如果失败)

    Examples:
        >>> result = await parse_document_from_url("http://example.com/doc.pdf")
        >>> if result["success"]:
        >>>     print(result["content"])
    """
    try:
        logger.info(f"开始解析文档: {url} (类型: {document_type})")

        # 下载文档
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()

        content_data = response.content
        detected_type = document_type or response.headers.get("content-type", "")

        logger.info(f"文档下载完成，大小: {len(content_data)} 字节，类型: {detected_type}")

        # 根据文档类型选择解析方法
        if detected_type == "application/pdf" or url.lower().endswith(".pdf"):
            # PDF 文档解析
            text_content = _pdf_processor.extract_text(content_data, filename="document.pdf")

            return {
                "success": True,
                "content": text_content,
                "document_type": "pdf",
                "size_bytes": len(content_data),
            }

        elif detected_type.startswith("image/") or any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            # 图片文件
            return {
                "success": True,
                "content": f"这是一张图片文件。\n\n图片URL: {url}\n\n请使用支持视觉的模型来分析这张图片的内容。",
                "document_type": "image",
                "image_url": url,
                "size_bytes": len(content_data),
            }

        elif detected_type == "text/plain" or url.lower().endswith(".txt"):
            # 纯文本文件
            try:
                text = content_data.decode('utf-8')
            except UnicodeDecodeError:
                text = content_data.decode('gbk', errors='ignore')
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVZSMldRPT06MTk4YTZlNjI=

            return {
                "success": True,
                "content": text,
                "document_type": "text",
                "size_bytes": len(content_data),
            }

        else:
            # 不支持的文档类型
            return {
                "success": False,
                "error": f"不支持的文档类型: {detected_type}。建议将文档转换为 PDF 或 TXT 格式。",
                "document_type": detected_type,
            }

    except httpx.HTTPError as e:
        logger.error(f"下载文档失败: {e}")
        return {
            "success": False,
            "error": f"文档下载失败: {str(e)}",
        }
    except Exception as e:
        logger.error(f"文档解析失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"文档解析失败: {str(e)}",
        }


# ============ 评审工具 ============

async def review_test_case_tool(
    test_case_content: str,
    review_aspects: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    测试用例评审工具（需要人工参与）
    
    该工具用于对生成的测试用例进行评审，会产生中断点让用户参与评审。
    评审方面包括：
    - completeness: 完整性 - 测试用例是否覆盖所有必要场景
    - accuracy: 准确性 - 测试步骤和预期结果是否准确
    - executability: 可执行性 - 测试用例是否可以实际执行
    - clarity: 清晰度 - 描述是否清晰易懂
    
    Args:
        test_case_content: 待评审的测试用例内容（JSON 格式字符串或文本描述）
        review_aspects: 需要评审的方面列表（可选）
            可选值：["completeness", "accuracy", "executability", "clarity"]
    
    Returns:
        dict: 包含评审结果的字典
            - success: bool, 是否成功
            - requires_human_input: bool, 是否需要人工输入
            - review_request: dict, 评审请求详情
            - message: str, 提示消息
    
    工作流程：
        1. AI 调用此工具提交评审请求
        2. Human-in-the-Loop 中间件检测到 requires_human_input 标志
        3. 系统产生中断，等待用户评审
        4. 用户在前端界面查看并提供反馈
        5. 反馈通过 API 提交后，执行继续
        6. AI 根据反馈更新测试用例
    
    示例：
        >>> result = await review_test_case_tool(
        ...     test_case_content='{"name": "登录测试", "steps": [...]}',
        ...     review_aspects=["completeness", "accuracy"]
        ... )
        >>> # 系统中断，等待用户反馈
        >>> # 用户通过 POST /api/v2/approvals/{id}/submit 提交反馈
        >>> # AI 获取反馈并继续执行
    """
    review_aspects = review_aspects or ["completeness", "accuracy", "executability", "clarity"]
    
    # 验证评审方面
    valid_aspects = ["completeness", "accuracy", "executability", "clarity"]
    invalid_aspects = [a for a in review_aspects if a not in valid_aspects]
    if invalid_aspects:
        logger.warning(f"发现无效的评审方面: {invalid_aspects}，将被忽略")
        review_aspects = [a for a in review_aspects if a in valid_aspects]
    
    logger.info(f"准备提交测试用例评审，评审方面: {review_aspects}")
    
    # 解析测试用例内容（如果是 JSON 字符串）
    import json
    try:
        if isinstance(test_case_content, str) and test_case_content.strip().startswith('{'):
            test_case_data = json.loads(test_case_content)
            test_case_name = test_case_data.get('name', '未命名测试用例')
        else:
            test_case_name = "测试用例"
    except json.JSONDecodeError:
        test_case_name = "测试用例"
    
    # 构建评审请求
    review_request = {
        "type": "test_case_review",
        "test_case_name": test_case_name,
        "content": test_case_content,
        "aspects": review_aspects,
        "aspect_descriptions": {
            "completeness": "测试用例是否覆盖所有必要场景（正常流程、异常流程、边界条件）",
            "accuracy": "测试步骤和预期结果是否准确、清晰",
            "executability": "测试用例是否可以实际执行，前置条件是否完整",
            "clarity": "测试用例描述是否清晰易懂，术语使用是否准确",
        },
        "instructions": f"请评审以下测试用例 \"{test_case_name}\"，关注以下方面：\n" + 
                        "\n".join([f"- {aspect}" for aspect in review_aspects]) +
                        f"\n\n测试用例内容：\n{test_case_content}",
    }
    
    # 返回评审请求，包含 requires_human_input 标志
    # Human-in-the-Loop 中间件会检测这个标志并产生中断
    return {
        "success": True,
        "requires_human_input": True,
        "review_request": review_request,
        "message": f"测试用例 \"{test_case_name}\" 已提交评审，等待用户反馈...",
        "pending": True,
    }


# ============ 思维导图生成工具 ============

async def generate_mindmap_tool(
    title: str,
    content: str,
    format: str = "markdown",
) -> dict[str, Any]:
    """
    生成思维导图工具
    
    将测试用例内容转换为思维导图格式，便于可视化和理解。
    支持多种输出格式。
    
    Args:
        title: 思维导图标题
        content: 要转换的内容（测试用例、测试计划等）
        format: 输出格式，可选值：
            - markdown: Markdown 格式（默认）
            - mermaid: Mermaid 图表格式
            - xmind: XMind 格式
    
    Returns:
        dict: 包含生成结果的字典
            - success: bool, 是否成功
            - mindmap_content: str, 思维导图内容
            - format: str, 输出格式
            - download_url: str, 下载链接（如果支持）
            - error: str, 错误信息（如果失败）
    
    Examples:
        >>> result = await generate_mindmap_tool(
        ...     title="用户登录功能测试用例",
        ...     content="...",
        ...     format="markdown"
        ... )
    """
    try:
        # MindMap MCP 服务器地址（从环境变量读取）
        mindmap_base_url = os.environ.get("MINDMAP_MCP_URL", "http://localhost:9003")
        
        logger.info(f"开始生成思维导图: {title} (格式: {format})")
        
        # 调用 MindMap MCP 服务器
        request_body = {
            "title": title,
            "content": content,
            "format": format,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{mindmap_base_url}/mindmap/generate",
                json=request_body
            )
            response.raise_for_status()
            mindmap_response = response.json()
        
        if mindmap_response.get("success"):
            return {
                "success": True,
                "mindmap_content": mindmap_response.get("mindmap_content", ""),
                "format": format,
                "download_url": mindmap_response.get("download_url"),
                "message": f"思维导图生成成功 (格式: {format})",
            }
        else:
            return {
                "success": False,
                "error": mindmap_response.get("error", "思维导图生成失败"),
            }
    
    except httpx.HTTPError as e:
        logger.error(f"MindMap 服务请求失败: {e}")
        return {
            "success": False,
            "error": f"MindMap 服务请求失败: {str(e)}",
        }
    except Exception as e:
        logger.error(f"思维导图生成失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"思维导图生成失败: {str(e)}",
        }


# ============ 需求分析工具 ============

async def save_requirement_analysis_tool(
    project_identifier: str,
    requirement_analysis_id: Optional[str] = None,
    title: Optional[str] = None,
    executive_summary: Optional[str] = None,
    functional_requirements: Optional[str] = None,
    non_functional_requirements: Optional[str] = None,
    user_stories: Optional[list] = None,
    acceptance_criteria: Optional[list] = None,
    dependencies: Optional[list] = None,
    risks: Optional[list] = None,
    recommendations: Optional[list] = None,
    priority_analysis: Optional[dict] = None,
    effort_estimation: Optional[dict] = None,
    quality_score: Optional[float] = None,
    completeness_score: Optional[float] = None,
    clarity_score: Optional[float] = None,
    consistency_score: Optional[float] = None,
    rag_context: Optional[dict] = None,
) -> dict[str, Any]:
    """
    保存需求分析结果到数据库。
    
    Args:
        project_identifier: 项目标识符（必填）
        requirement_analysis_id: 需求分析 ID（更新时必填）
        title: 需求分析标题
        executive_summary: 需求概述
        functional_requirements: 功能需求分析
        non_functional_requirements: 非功能需求分析
        user_stories: 用户故事列表
        acceptance_criteria: 验收标准列表
        dependencies: 依赖关系
        risks: 风险评估
        recommendations: 建议和改进意见
        priority_analysis: 优先级分析
        effort_estimation: 工作量评估
        quality_score: 总体质量评分（0-100）
        completeness_score: 完整性评分（0-100）
        clarity_score: 清晰度评分（0-100）
        consistency_score: 一致性评分（0-100）
        rag_context: RAG 检索的上下文信息
    
    Returns:
        包含保存结果的字典
    """
    try:
        # 构建请求数据
        data = {
            "title": title,
            "executive_summary": executive_summary,
            "functional_requirements": functional_requirements,
            "non_functional_requirements": non_functional_requirements,
            "user_stories": user_stories or [],
            "acceptance_criteria": acceptance_criteria or [],
            "dependencies": dependencies or [],
            "risks": risks or [],
            "recommendations": recommendations or [],
            "priority_analysis": priority_analysis,
            "effort_estimation": effort_estimation,
            "quality_score": quality_score,
            "completeness_score": completeness_score,
            "clarity_score": clarity_score,
            "consistency_score": consistency_score,
            "rag_context": rag_context,
        }
        
        # 移除 None 值
        data = {k: v for k, v in data.items() if v is not None}
        
        if requirement_analysis_id:
            # 更新现有需求分析
            url = get_api_url(f"/requirement-analysis/{requirement_analysis_id}")
            response = await make_http_request("PUT", url, json_data=data)
            return {
                "success": True,
                "requirement_analysis_id": requirement_analysis_id,
                "message": "需求分析已更新",
                "data": response
            }
        else:
            # 创建新需求分析
            url = get_api_url(f"/projects/{project_identifier}/requirement-analysis")
            response = await make_http_request("POST", url, json_data=data)
            return {
                "success": True,
                "requirement_analysis_id": response.get("id"),
                "message": "需求分析已创建",
                "data": response
            }
    
    except Exception as e:
        logger.error(f"保存需求分析失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"保存需求分析失败: {str(e)}"
        }


# ============ 缺陷分析工具 ============

async def save_defect_analysis_tool(
    project_identifier: str,
    defect_analysis_id: Optional[str] = None,
    title: Optional[str] = None,
    executive_summary: Optional[str] = None,
    defect_classification: Optional[dict] = None,
    root_cause_analysis: Optional[str] = None,
    impact_analysis: Optional[str] = None,
    reproduction_steps: Optional[list] = None,
    affected_modules: Optional[list] = None,
    fix_suggestions: Optional[list] = None,
    test_recommendations: Optional[list] = None,
    prevention_measures: Optional[list] = None,
    similar_defects: Optional[list] = None,
    trend_analysis: Optional[dict] = None,
    frequency_analysis: Optional[dict] = None,
    quality_score: Optional[float] = None,
    completeness_score: Optional[float] = None,
    clarity_score: Optional[float] = None,
    actionability_score: Optional[float] = None,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    defect_type: Optional[str] = None,
    rag_context: Optional[dict] = None,
) -> dict[str, Any]:
    """
    保存缺陷分析结果到数据库。
    
    Args:
        project_identifier: 项目标识符（必填）
        defect_analysis_id: 缺陷分析 ID（更新时必填）
        title: 缺陷分析标题
        executive_summary: 缺陷概述
        defect_classification: 缺陷分类分析
        root_cause_analysis: 根本原因分析
        impact_analysis: 影响分析
        reproduction_steps: 复现步骤
        affected_modules: 受影响的模块
        fix_suggestions: 修复建议
        test_recommendations: 测试建议
        prevention_measures: 预防措施
        similar_defects: 相似缺陷
        trend_analysis: 趋势分析
        frequency_analysis: 频率分析
        quality_score: 总体质量评分（0-100）
        completeness_score: 完整性评分（0-100）
        clarity_score: 清晰度评分（0-100）
        actionability_score: 可操作性评分（0-100）
        severity: 严重程度
        priority: 优先级
        defect_type: 缺陷类型
        rag_context: RAG 检索的上下文信息
    
    Returns:
        包含保存结果的字典
    """
    try:
        # 构建请求数据
        data = {
            "title": title,
            "executive_summary": executive_summary,
            "defect_classification": defect_classification,
            "root_cause_analysis": root_cause_analysis,
            "impact_analysis": impact_analysis,
            "reproduction_steps": reproduction_steps or [],
            "affected_modules": affected_modules or [],
            "fix_suggestions": fix_suggestions or [],
            "test_recommendations": test_recommendations or [],
            "prevention_measures": prevention_measures or [],
            "similar_defects": similar_defects or [],
            "trend_analysis": trend_analysis,
            "frequency_analysis": frequency_analysis,
            "quality_score": quality_score,
            "completeness_score": completeness_score,
            "clarity_score": clarity_score,
            "actionability_score": actionability_score,
            "severity": severity,
            "priority": priority,
            "defect_type": defect_type,
            "rag_context": rag_context,
        }
        
        # 移除 None 值
        data = {k: v for k, v in data.items() if v is not None}
        
        if defect_analysis_id:
            # 更新现有缺陷分析
            url = get_api_url(f"/defect-analysis/{defect_analysis_id}")
            response = await make_http_request("PUT", url, json_data=data)
            return {
                "success": True,
                "defect_analysis_id": defect_analysis_id,
                "message": "缺陷分析已更新",
                "data": response
            }
        else:
            # 创建新缺陷分析
            url = get_api_url(f"/projects/{project_identifier}/defect-analysis")
            response = await make_http_request("POST", url, json_data=data)
            return {
                "success": True,
                "defect_analysis_id": response.get("id"),
                "message": "缺陷分析已创建",
                "data": response
            }
    
    except Exception as e:
        logger.error(f"保存缺陷分析失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"保存缺陷分析失败: {str(e)}"
        }


# ============ 工具列表 ============

# 测试用例工具列表，供测试用例生成智能体使用
TESTCASE_TOOLS = [
    create_test_case_tool,
    update_test_case_tool,
    batch_create_test_cases_tool,
    parse_document_from_url,  # 文档解析工具
    rag_query_tool,  # RAG 检索工具
    review_test_case_tool,  # 评审工具（需要人工参与）
    generate_mindmap_tool,  # 思维导图生成工具
]

# 需求分析工具列表，供需求分析智能体使用
REQUIREMENT_ANALYSIS_TOOLS = [
    save_requirement_analysis_tool,
    parse_document_from_url,  # 文档解析工具
    rag_query_tool,  # RAG 检索工具
]

# 缺陷分析工具列表，供缺陷分析智能体使用
DEFECT_ANALYSIS_TOOLS = [
    save_defect_analysis_tool,
    parse_document_from_url,  # 文档解析工具
    rag_query_tool,  # RAG 检索工具
]
