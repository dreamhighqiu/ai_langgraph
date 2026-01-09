"""
智能体工具集

提供测试用例创建、RAG检索等工具函数，供智能体调用
直接调用 Service 层，避免 HTTP 认证问题

架构参考: ai-test-management 项目
"""

import httpx
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool

from config.env import AppConfig
from utils.log_util import logger


# ============ 配置 ============

# API 基础 URL (用于 RAG 等外部服务)
API_BASE_URL = f"http://127.0.0.1:{AppConfig.app_port}"
HTTP_TIMEOUT = 30.0


# ============ 辅助函数 ============

def get_api_url(path: str) -> str:
    """构建完整的 API URL"""
    return f"{API_BASE_URL}{path}"


def get_current_user_id() -> int:
    """
    获取当前用户ID（从 RequestContext 获取）
    
    用于工具函数中获取当前登录用户ID，避免 HTTP 认证问题。
    
    Returns:
        int: 当前用户ID，如果无法获取则返回默认值 1（系统用户）
    """
    try:
        from common.context import RequestContext
        current_user = RequestContext.get_current_user()
        if current_user and hasattr(current_user, 'user_id'):
            return current_user.user_id
        elif current_user and hasattr(current_user, 'user') and current_user.user:
            return current_user.user.user_id
        else:
            logger.warning("无法获取当前用户ID，使用默认值 1")
            return 1
    except Exception as e:
        logger.warning(f"获取当前用户ID失败: {str(e)}，使用默认值 1")
        return 1


def _normalize_mcp_sse_url(url: str) -> str:
    """
    规范化 MCP SSE 服务 URL。

    兼容传入 base host（如 http://localhost:9002）或完整 SSE 路径（如 http://localhost:9002/sse）。
    """
    normalized = (url or "").strip().rstrip("/")
    if not normalized:
        return "/sse"
    return normalized if normalized.endswith("/sse") else f"{normalized}/sse"


def _pick_mcp_tool(tools: list, tool_name: str):
    """从 MCP tools 列表中选取指定工具（兼容带前缀的名称）。"""
    for tool in tools:
        name = getattr(tool, "name", "") or ""
        if name == tool_name:
            return tool
    for tool in tools:
        name = getattr(tool, "name", "") or ""
        if name.endswith(tool_name) or name.endswith(f".{tool_name}") or name.endswith(f"__{tool_name}"):
            return tool
    return None


async def make_http_request(
    method: str,
    url: str,
    json_data: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: Optional[float] = None,
    headers: Optional[dict] = None,
) -> dict:
    """
    发送 HTTP 请求的通用函数
    
    Args:
        method: HTTP 方法（GET, POST, PATCH, DELETE）
        url: 完整的 URL
        json_data: JSON 请求体
        params: URL 查询参数
        timeout: 超时时间（秒）
        headers: 请求头
        
    Returns:
        dict: 响应数据
    """
    timeout_value = timeout or HTTP_TIMEOUT
    
    try:
        async with httpx.AsyncClient(timeout=timeout_value) as client:
            response = await client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail") or error_json.get("msg") or error_detail
        except Exception:
            pass
        raise Exception(f"HTTP {e.response.status_code}: {error_detail}")
    except httpx.RequestError as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"请求失败: {str(e)}")


# ============ 工具函数 ============

@tool
async def create_test_case_tool(
    project_id: int,
    name: str,
    folder_id: Optional[int] = None,
    description: Optional[str] = None,
    module: Optional[str] = None,
    case_type: str = "functional",
    priority: str = "medium",
    status: str = "draft",
    preconditions: Optional[str] = None,
    test_case_steps: Optional[List[Dict[str, str]]] = None,
    expected_result: Optional[str] = None,
    test_data: Optional[str] = None,
    tags: Optional[List[str]] = None,
    template: str = "test_case",
    feature: Optional[str] = None,
    scenario: Optional[str] = None,
    background: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建测试用例工具（直接调用 Service 层）
    
    该工具直接调用测试用例 Service 来创建新的测试用例，绕过 HTTP 认证。
    支持普通测试用例和 BDD 测试用例两种模板。
    
    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        name: 测试用例名称（必填）
        folder_id: 文件夹ID（可选，从上下文自动获取，如不传则创建到项目根目录）
        description: 测试用例描述
        module: 所属模块
        case_type: 测试类型（functional, regression, smoke, performance, security等）
        priority: 优先级（critical, high, medium, low）
        status: 状态（draft, active, in_review, approved, deprecated）
        preconditions: 前置条件
        test_case_steps: 测试步骤列表，每个步骤包含：
            - step: 操作步骤描述（必填）
            - expected: 预期结果（可选）
        expected_result: 整体预期结果
        test_data: 测试数据
        tags: 标签列表
        template: 模板类型（test_case: 普通测试用例, test_case_bdd: BDD测试用例）
        feature: BDD Feature 描述（BDD 测试用例使用）
        scenario: BDD Scenario 描述（BDD 测试用例使用）
        background: BDD Background 描述（BDD 测试用例使用）
        
    Returns:
        dict: 包含创建结果的字典
            - success: 是否成功
            - data: 创建的测试用例信息（如果成功）
            - error: 错误信息（如果失败）
            
    Examples:
        # 创建普通测试用例
        result = await create_test_case_tool(
            project_id=1,
            name="用户登录功能测试",
            folder_id=10,
            description="验证用户登录功能是否正常",
            priority="high",
            case_type="functional",
            test_case_steps=[
                {"step": "打开登录页面", "expected": "页面正常显示"},
                {"step": "输入用户名和密码", "expected": "输入框接受输入"},
                {"step": "点击登录按钮", "expected": "成功登录并跳转到首页"}
            ]
        )
        
        # 创建 BDD 测试用例
        result = await create_test_case_tool(
            project_id=1,
            name="用户登录场景",
            template="test_case_bdd",
            feature="用户认证",
            scenario="用户使用正确的凭据登录",
            background="Given 用户已注册"
        )
    """
    try:
        # 参数验证
        if not project_id:
            return {
                "success": False,
                "error": "project_id 是必填参数，请确保从上下文中获取",
                "message": "创建测试用例失败：缺少项目ID"
            }
        
        if not name:
            return {
                "success": False,
                "error": "name 是必填参数",
                "message": "创建测试用例失败：缺少测试用例名称"
            }
        
        # 直接调用 Service 层，绕过 HTTP 认证
        from module_testing.service.test_case_service import TestCaseService
        from module_testing.entity.vo.test_case_vo import TestCaseCreateVO, TestCaseStepVO
        from config.get_db import get_db_session
        
        # 处理测试步骤 - 转换为 VO 对象
        processed_steps = None
        if test_case_steps:
            processed_steps = []
            for idx, step in enumerate(test_case_steps, start=1):
                if isinstance(step, dict):
                    # 兼容多种格式：step/expected 或 action/expected 或 action/result
                    action = step.get('step') or step.get('action', '')
                    expected = step.get('expected') or step.get('result', '')
                    processed_steps.append(TestCaseStepVO(
                        step_number=idx,
                        action=action,
                        expected=expected
                    ))
        
        # 构建 VO 对象
        test_case_vo = TestCaseCreateVO(
            case_name=name,
            project_id=project_id,
            folder_id=folder_id if folder_id else None,
            description=description,
            module=module,
            case_type=case_type,
            priority=priority,
            status=status,
            preconditions=preconditions,
            expected_results=expected_result,
            test_data=test_data,
            tags=tags,
            template=template,
            test_case_steps=processed_steps,
        )
            
        # 根据模板类型添加相应字段
        if template == "test_case_bdd":
            if feature:
                test_case_vo.feature = feature
            if scenario:
                test_case_vo.scenario = scenario
            if background:
                test_case_vo.background = background
        
        # 调用 Service 创建测试用例
        service = TestCaseService()
        
        async with get_db_session() as db:
            # 使用固定的 AI 创建者标识
            # auto_commit=False 让 get_db_session() 的上下文管理器处理 commit
            result = await service.create_test_case(
                db, test_case_vo, "AI助手", auto_commit=False
            )
            
            # 确保数据已刷新（在 commit 之前）
            await db.flush()
            
            logger.info(f"AI 成功创建测试用例: {result.case_identifier} - {name} (ID: {result.case_id})")
        
        return {
            "success": True,
                "data": {
                    "case_id": result.case_id,
                    "case_identifier": result.case_identifier,
                    "case_name": result.case_name,
                },
                "message": f"✅ 测试用例 '{name}' (ID: {result.case_id}, 标识: {result.case_identifier}) 创建成功"
        }

    except Exception as e:
        logger.error(f"创建测试用例失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ 创建测试用例失败: {str(e)}"
        }


@tool
async def update_test_case_tool(
    case_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    module: Optional[str] = None,
    case_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    folder_id: Optional[int] = None,
    preconditions: Optional[str] = None,
    test_case_steps: Optional[List[Dict[str, str]]] = None,
    expected_result: Optional[str] = None,
    test_data: Optional[str] = None,
    tags: Optional[List[str]] = None,
    feature: Optional[str] = None,
    scenario: Optional[str] = None,
    background: Optional[str] = None,
) -> Dict[str, Any]:
    """
    更新测试用例工具（直接调用 Service 层）
    
    该工具直接调用测试用例 Service 来更新现有测试用例的信息。
    所有字段都是可选的，只更新提供的字段。

    Args:
        case_id: 测试用例ID（必填）
        name: 测试用例名称
        description: 测试用例描述
        module: 所属模块
        case_type: 测试类型
        priority: 优先级（critical, high, medium, low）
        status: 状态（draft, active, in_review, approved, deprecated）
        folder_id: 所属文件夹ID（用于移动测试用例）
        preconditions: 前置条件
        test_case_steps: 测试步骤列表
        expected_result: 预期结果
        test_data: 测试数据
        tags: 标签列表
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
            case_id=123,
            priority="critical",
            status="active"
        )

        # 更新测试步骤
        result = await update_test_case_tool(
            case_id=123,
            test_case_steps=[
                {"step": "新步骤1", "expected": "预期结果1"},
                {"step": "新步骤2", "expected": "预期结果2"}
            ]
        )
    """
    try:
        from module_testing.service.test_case_service import TestCaseService
        from module_testing.entity.vo.test_case_vo import TestCaseUpdateVO
        from config.get_db import get_db_session
        
        # 构建更新 VO，只包含非 None 的字段
        update_data = {}

        if name is not None:
            update_data["case_name"] = name
        if description is not None:
            update_data["description"] = description
        if module is not None:
            update_data["module"] = module
        if case_type is not None:
            update_data["case_type"] = case_type
        if priority is not None:
            update_data["priority"] = priority
        if status is not None:
            update_data["status"] = status
        if folder_id is not None:
            update_data["folder_id"] = folder_id
        if preconditions is not None:
            update_data["preconditions"] = preconditions
        if test_case_steps is not None:
            update_data["test_case_steps"] = test_case_steps
        if expected_result is not None:
            update_data["expected_result"] = expected_result
        if test_data is not None:
            update_data["test_data"] = test_data
        if tags is not None:
            update_data["tags"] = tags
        if feature is not None:
            update_data["feature"] = feature
        if scenario is not None:
            update_data["scenario"] = scenario
        if background is not None:
            update_data["background"] = background

        # 如果没有任何字段需要更新，返回错误
        if not update_data:
            return {
                "success": False,
                "error": "没有提供任何需要更新的字段",
                "message": "更新测试用例失败：没有提供任何需要更新的字段"
            }

        # 创建 VO 对象
        test_case_vo = TestCaseUpdateVO(**update_data)

        # 调用 Service 更新测试用例
        service = TestCaseService()
        
        async with get_db_session() as db:
            result = await service.update_test_case(
                db, case_id, test_case_vo, "ai_agent"
        )

        return {
            "success": True,
                "data": {
                    "case_id": result.case_id,
                },
            "message": f"测试用例 {case_id} 更新成功"
        }

    except Exception as e:
        logger.error(f"更新测试用例失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"更新测试用例失败: {str(e)}"
        }


@tool
async def batch_create_test_cases_tool(
    project_id: int,
    test_cases: List[Dict[str, Any]],
    folder_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    批量创建测试用例工具（直接调用 Service 层）
    
    该工具可以一次性创建多个测试用例，提高效率。
    每个测试用例的参数与 create_test_case_tool 相同。

    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        test_cases: 测试用例列表，每个元素是一个包含测试用例信息的字典，包含以下字段：
            - name: 测试用例名称（必填）
            - description: 测试用例描述（可选）
            - preconditions: 前置条件（可选）
            - priority: 优先级（可选，默认 medium）
            - status: 状态（可选，默认 draft）
            - case_type: 测试类型（可选，默认 functional）
            - tags: 标签列表（可选）
            - template: 模板类型（可选，默认 test_case）
            - test_case_steps: 测试步骤列表（可选）
            - feature: BDD Feature 描述（可选）
            - scenario: BDD Scenario 描述（可选）
            - background: BDD Background 描述（可选）
        folder_id: 文件夹ID（可选，从上下文自动获取）

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
            project_id=1,
            folder_id=10,
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
        
        from module_testing.service.test_case_service import TestCaseService
        from module_testing.entity.vo.test_case_vo import TestCaseCreateVO, TestCaseStepVO
        from config.get_db import get_db_session
        
        results = []
        succeeded = 0
        failed = 0
        
        service = TestCaseService()
        
        # 使用同一个数据库会话批量创建
        async with get_db_session() as db:
            for index, tc in enumerate(test_cases):
                try:
                    name = tc.get("name") or tc.get("case_name")
                    if not name:
                        results.append({
                            "index": index,
                            "success": False,
                            "error": "测试用例名称不能为空"
                        })
                        failed += 1
                        continue
                    
                    # 处理测试步骤 - 转换为 VO 对象
                    raw_steps = tc.get("test_case_steps")
                    processed_steps = None
                    if raw_steps:
                        processed_steps = []
                        for idx, step in enumerate(raw_steps, start=1):
                            if isinstance(step, dict):
                                action = step.get('step') or step.get('action', '')
                                expected = step.get('expected') or step.get('result', '')
                                processed_steps.append(TestCaseStepVO(
                                    step_number=idx,
                                    action=action,
                                    expected=expected
                                ))
                    
                    # 构建 VO 对象
                    test_case_vo = TestCaseCreateVO(
                        case_name=name,
                        project_id=project_id,
                        folder_id=folder_id or tc.get("folder_id"),
                        description=tc.get("description"),
                        module=tc.get("module"),
                        case_type=tc.get("case_type", "functional"),
                        priority=tc.get("priority", "medium"),
                        status=tc.get("status", "draft"),
                        preconditions=tc.get("preconditions"),
                        expected_results=tc.get("expected_result"),
                        test_data=tc.get("test_data"),
                        tags=tc.get("tags"),
                        template=tc.get("template", "test_case"),
                        test_case_steps=processed_steps,
                        feature=tc.get("feature"),
                        scenario=tc.get("scenario"),
                        background=tc.get("background"),
                    )
                    
                    # 调用 Service 创建
                    # auto_commit=False 让 get_db_session() 的上下文管理器处理 commit
                    result = await service.create_test_case(
                        db, test_case_vo, "AI助手", auto_commit=False
                    )
                    
                    # 确保数据已刷新
                    await db.flush()
                    
                    logger.info(f"AI 批量创建测试用例成功: {result.case_identifier} - {name} (ID: {result.case_id})")
                    
                    results.append({
                        "index": index,
                        "name": name,
                        "success": True,
                        "data": {
                            "case_id": result.case_id,
                            "case_identifier": result.case_identifier,
                        },
                        "message": f"✅ 测试用例 '{name}' 创建成功"
                    })
                    succeeded += 1
                    
                except Exception as e:
                    results.append({
                        "index": index,
                        "name": tc.get("name") or tc.get("case_name", "未知"),
                        "success": False,
                        "error": str(e)
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
        logger.error(f"批量创建测试用例失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": f"批量创建测试用例失败: {str(e)}"
        }


@tool
async def rag_query_tool(
    query: str,
    mode: str = "mix",
    top_k: int = 10,
    chunk_top_k: int = 5,
    enable_rerank: bool = True,
) -> Dict[str, Any]:
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
        import os
        # RAG MCP 服务器地址（从环境变量读取）；默认使用 SSE 传输
        rag_mcp_url = _normalize_mcp_sse_url(
            os.environ.get("RAG_MCP_URL", "http://localhost:9002/sse")
        )

        logger.info(f"开始 RAG 检索: {query} (模式: {mode})")

        from langchain_mcp_adapters.client import MultiServerMCPClient

        mcp_client = MultiServerMCPClient(
            {
                "rag": {
                    "url": rag_mcp_url,
                    "transport": "sse",
                }
            }
        )
        mcp_tools = list(await mcp_client.get_tools())
        tool = _pick_mcp_tool(mcp_tools, "rag_query_data_json") or _pick_mcp_tool(
            mcp_tools, "rag_query_data"
        )

        if tool is None:
            return {
                "success": False,
                "error": "未找到 RAG MCP 工具（rag_query_data_json / rag_query_data）",
                "context": "",
                "entities": [],
                "chunks": [],
                "metadata": {},
            }

        raw = await tool.ainvoke(
            {
                "query": query,
                "mode": mode,
                "top_k": top_k,
                "chunk_top_k": chunk_top_k,
                "enable_rerank": enable_rerank,
            }
        )

        tool_name = str(getattr(tool, "name", "") or "")
        if tool_name == "rag_query_data_json" or (isinstance(raw, str) and raw.strip().startswith("{")):
            # JSON 格式响应
            import json
            try:
                if isinstance(raw, str):
                    result = json.loads(raw)
                else:
                    result = raw
                
                if result.get("status") == "failure":
                    return {
                        "success": False,
                        "error": result.get("message", "RAG 检索失败"),
                        "context": "",
                        "entities": [],
                        "chunks": [],
                        "metadata": {},
                    }
                
                data = result.get("data", {})
                context_parts = []
                
                # 构建上下文文本
                if data.get("entities"):
                    context_parts.append(f"实体 ({len(data['entities'])} 个):")
                    for entity in data["entities"][:5]:
                        context_parts.append(f"  - {entity.get('entity_name', '')}: {entity.get('description', '')}")
                
                if data.get("chunks"):
                    context_parts.append(f"\n相关文档片段 ({len(data['chunks'])} 个):")
                    for chunk in data["chunks"][:3]:
                        content = chunk.get("content", "")[:200]
                        context_parts.append(f"  - {content}...")
                
                context_text = "\n".join(context_parts) if context_parts else "未找到相关信息"
                
                return {
                    "success": True,
                    "context": context_text,
                    "entities": data.get("entities", []),
                    "chunks": data.get("chunks", []),
                    "metadata": result.get("metadata", {}),
                    "message": "RAG 检索成功"
                }
            except json.JSONDecodeError:
                # 如果不是 JSON，当作文本处理
                return {
                    "success": True,
                    "context": str(raw),
                    "entities": [],
                    "chunks": [],
                    "metadata": {},
                    "message": "RAG 检索成功"
                }
        else:
            # 文本格式响应
            return {
                "success": True,
                "context": str(raw),
                "entities": [],
                "chunks": [],
                "metadata": {},
            "message": "RAG 检索成功"
        }

    except httpx.HTTPError as e:
        logger.error(f"RAG MCP 服务请求失败: {e}")
        return {
            "success": False,
            "error": f"RAG MCP 服务请求失败: {str(e)}",
            "context": "",
            "entities": [],
            "chunks": [],
            "metadata": {},
        }
    except Exception as e:
        logger.error(f"RAG 检索失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "context": "",
            "entities": [],
            "chunks": [],
            "metadata": {},
            "message": f"RAG 检索失败: {str(e)}"
        }


@tool
async def save_requirement_analysis_tool(
    project_id: int,
    requirement_analysis_id: Optional[int] = None,
    analysis_name: Optional[str] = None,
    executive_summary: Optional[str] = None,
    functional_requirements: Optional[str] = None,
    non_functional_requirements: Optional[str] = None,
    user_stories: Optional[List[Dict[str, Any]]] = None,
    acceptance_criteria: Optional[List[Dict[str, Any]]] = None,
    dependencies: Optional[List[Dict[str, Any]]] = None,
    risks: Optional[List[Dict[str, Any]]] = None,
    recommendations: Optional[List[Dict[str, Any]]] = None,
    priority_analysis: Optional[Dict[str, Any]] = None,
    effort_estimation: Optional[Dict[str, Any]] = None,
    quality_completeness: Optional[float] = None,
    quality_clarity: Optional[float] = None,
    quality_consistency: Optional[float] = None,
    quality_testability: Optional[float] = None,
    quality_overall: Optional[float] = None,
    rag_context: Optional[str] = None,
    use_rag: int = 0,
    mindmap_data: Optional[Dict[str, Any]] = None,
    mindmap_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: str = "completed",
) -> Dict[str, Any]:
    """
    保存需求分析结果到数据库。
    
    该工具直接调用需求分析 Service 来保存分析结果，绕过 HTTP 认证。
    支持创建新需求和更新现有需求。

    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        requirement_analysis_id: 需求分析 ID（更新时必填，创建时留空）
        analysis_name: 需求分析名称/标题
        executive_summary: 需求概述
        functional_requirements: 功能需求分析（JSON 字符串或文本）
        non_functional_requirements: 非功能需求分析（JSON 字符串或文本）
        user_stories: 用户故事列表，每个元素包含：
            - story_id: 故事ID（可选）
            - title: 故事标题
            - description: 故事描述
            - acceptance_criteria: 验收标准
            - priority: 优先级
        acceptance_criteria: 验收标准列表，每个元素包含：
            - criterion_id: 标准ID（可选）
            - description: 标准描述
            - priority: 优先级
        dependencies: 依赖关系列表，每个元素包含：
            - dependency_id: 依赖ID（可选）
            - type: 依赖类型（前置/后置/并行）
            - description: 依赖描述
            - related_requirement: 相关需求
        risks: 风险评估列表，每个元素包含：
            - risk_id: 风险ID（可选）
            - type: 风险类型
            - description: 风险描述
            - probability: 发生概率
            - impact: 影响程度
            - mitigation: 缓解措施
        recommendations: 建议和改进意见列表，每个元素包含：
            - recommendation_id: 建议ID（可选）
            - type: 建议类型
            - description: 建议描述
            - priority: 优先级
        priority_analysis: 优先级分析字典，包含：
            - high_priority: 高优先级需求列表
            - medium_priority: 中优先级需求列表
            - low_priority: 低优先级需求列表
            - rationale: 优先级判断依据
        effort_estimation: 工作量评估字典，包含：
            - total_effort: 总工作量（人天）
            - breakdown: 工作量分解
            - assumptions: 评估假设
        quality_completeness: 完整性评分（0-100）
        quality_clarity: 清晰度评分（0-100）
        quality_consistency: 一致性评分（0-100）
        quality_testability: 可测试性评分（0-100）
        quality_overall: 总体质量评分（0-100）
        rag_context: RAG 检索的上下文信息（JSON 字符串）
        use_rag: 是否使用 RAG（0=否，1=是）
        mindmap_data: 思维导图数据（JSON 对象）
        mindmap_url: 思维导图图片 URL
        tags: 标签列表
        status: 状态（draft/analyzing/completed/failed，默认 completed）

    Returns:
        dict: 包含保存结果的字典
            - success: bool, 是否成功
            - requirement_analysis_id: int, 需求分析 ID
            - analysis_name: str, 分析名称
            - message: str, 提示消息
            - error: str, 错误信息（如果失败）
    
    Examples:
        # 创建新需求分析
        result = await save_requirement_analysis_tool(
            project_id=1,
            analysis_name="用户登录功能需求分析",
            executive_summary="分析用户登录功能的需求...",
            functional_requirements='{"login_methods": ["username", "email"]}',
            quality_overall=85.5
        )
        
        # 更新现有需求分析
        result = await save_requirement_analysis_tool(
            project_id=1,
            requirement_analysis_id=123,
            analysis_name="更新后的分析名称",
            quality_overall=90.0
        )
    """
    try:
        import json
        from module_testing.service.requirement_analysis_service import RequirementAnalysisService
        from module_testing.entity.vo.requirement_analysis_vo import RequirementAnalysisVO
        from config.get_db import get_db_session
        
        # 参数验证
        if not project_id:
            return {
                "success": False,
                "error": "project_id 是必填参数，请确保从上下文中获取",
                "message": "保存需求分析失败：缺少项目ID"
            }
        
        if not analysis_name and not requirement_analysis_id:
            return {
                "success": False,
                "error": "创建新需求分析时，analysis_name 是必填参数",
                "message": "保存需求分析失败：缺少分析名称"
        }

        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 构建 VO 对象
        requirement_vo = RequirementAnalysisVO(
            project_id=project_id,
            requirement_name=analysis_name or f"需求分析_{requirement_analysis_id}",
            requirement_type="functional",  # 默认功能需求
            priority="medium",  # 默认中等优先级
            status=status,
            module=None,  # 可以从上下文获取
            description=executive_summary,
            acceptance_criteria=json.dumps(acceptance_criteria, ensure_ascii=False) if acceptance_criteria else None,
            functional_requirements=json.dumps(functional_requirements, ensure_ascii=False) if isinstance(functional_requirements, dict) else functional_requirements,
            non_functional_requirements=json.dumps(non_functional_requirements, ensure_ascii=False) if isinstance(non_functional_requirements, dict) else non_functional_requirements,
            business_rules=None,  # 可以从其他字段映射
            dependencies=json.dumps(dependencies, ensure_ascii=False) if dependencies else None,
            stakeholders=None,  # 可以从其他字段映射
        )
        
        # 调用 Service 保存需求分析
        service = RequirementAnalysisService()
        
        async with get_db_session() as db:
            if requirement_analysis_id:
                # 更新现有需求分析
                result = await service.update_requirement(
                    db, requirement_analysis_id, requirement_vo, user_id
                )
                logger.info(f"AI 成功更新需求分析: {requirement_analysis_id} - {result.requirement_identifier}")
                
                return {
                    "success": True,
                    "requirement_analysis_id": requirement_analysis_id,
                    "analysis_name": result.requirement_name,
                    "requirement_identifier": result.requirement_identifier,
                    "message": f"✅ 需求分析 '{result.requirement_name}' (ID: {requirement_analysis_id}) 更新成功"
                }
            else:
                # 创建新需求分析
                result = await service.create_requirement(
                    db, requirement_vo, user_id
                )
                logger.info(f"AI 成功创建需求分析: {result.requirement_identifier} - {result.requirement_name} (ID: {result.requirement_id})")
                
                return {
                    "success": True,
                    "requirement_analysis_id": result.requirement_id,
                    "analysis_name": result.requirement_name,
                    "requirement_identifier": result.requirement_identifier,
                    "message": f"✅ 需求分析 '{result.requirement_name}' (ID: {result.requirement_id}, 标识: {result.requirement_identifier}) 创建成功"
                }

    except Exception as e:
        logger.error(f"保存需求分析失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"保存需求分析失败: {str(e)}"
        }


@tool
async def save_defect_analysis_tool(
    project_id: int,
    defect_analysis_id: Optional[int] = None,
    analysis_name: Optional[str] = None,
    defect_title: Optional[str] = None,
    defect_description: Optional[str] = None,
    executive_summary: Optional[str] = None,
    root_cause_analysis: Optional[Dict[str, Any]] = None,
    impact_analysis: Optional[Dict[str, Any]] = None,
    reproduction_steps: Optional[List[Dict[str, Any]]] = None,
    affected_modules: Optional[List[str]] = None,
    fix_suggestions: Optional[List[Dict[str, Any]]] = None,
    test_suggestions: Optional[List[Dict[str, Any]]] = None,
    prevention_measures: Optional[List[Dict[str, Any]]] = None,
    similar_defects: Optional[List[Dict[str, Any]]] = None,
    severity: str = "medium",
    priority: str = "medium",
    defect_type: Optional[str] = None,
    category: Optional[str] = None,
    affected_phase: Optional[str] = None,
    detection_phase: Optional[str] = None,
    fix_status: Optional[str] = None,
    fix_time_estimate: Optional[str] = None,
    rag_context: Optional[str] = None,
    use_rag: int = 0,
    mindmap_data: Optional[Dict[str, Any]] = None,
    mindmap_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: str = "completed",
    knowledge_id: Optional[int] = None,
    defect_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    保存缺陷分析结果到数据库。
    
    该工具直接调用缺陷分析 Service 来保存分析结果，绕过 HTTP 认证。
    支持创建新缺陷分析和更新现有缺陷分析。

    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        defect_analysis_id: 缺陷分析 ID（更新时必填，创建时留空）
        analysis_name: 缺陷分析名称/标题
        defect_title: 缺陷标题
        defect_description: 缺陷描述
        executive_summary: 缺陷概述
        root_cause_analysis: 根本原因分析字典，包含：
            - primary_cause: 主要原因
            - contributing_factors: 促成因素列表
            - analysis_method: 分析方法
            - evidence: 证据
        impact_analysis: 影响分析字典，包含：
            - affected_areas: 受影响区域列表
            - severity_level: 严重程度级别
            - business_impact: 业务影响
            - technical_impact: 技术影响
            - user_impact: 用户影响
        reproduction_steps: 复现步骤列表，每个元素包含：
            - step_number: 步骤编号
            - description: 步骤描述
            - expected_result: 预期结果
            - actual_result: 实际结果
        affected_modules: 受影响模块列表（字符串列表）
        fix_suggestions: 修复建议列表，每个元素包含：
            - suggestion_id: 建议ID（可选）
            - description: 建议描述
            - priority: 优先级
            - estimated_effort: 预估工作量
        test_suggestions: 测试建议列表，每个元素包含：
            - suggestion_id: 建议ID（可选）
            - test_type: 测试类型
            - description: 测试建议描述
            - priority: 优先级
        prevention_measures: 预防措施列表，每个元素包含：
            - measure_id: 措施ID（可选）
            - type: 措施类型
            - description: 措施描述
            - implementation: 实施方法
        similar_defects: 相似缺陷列表，每个元素包含：
            - defect_id: 缺陷ID
            - similarity_score: 相似度评分
            - description: 相似性描述
        severity: 严重程度（critical/high/medium/low，默认 medium）
        priority: 优先级（urgent/high/medium/low，默认 medium）
        defect_type: 缺陷类型（functional/performance/security/ui/compatibility等）
        category: 详细分类
        affected_phase: 影响阶段（requirements/design/development/testing/deployment）
        detection_phase: 发现阶段（requirements/design/development/testing/deployment/production）
        fix_status: 修复状态（pending/in_progress/fixed/verified，可选）
        fix_time_estimate: 预计修复时间（如 "2 days"）
        rag_context: RAG 检索的上下文信息（JSON 字符串）
        use_rag: 是否使用 RAG（0=否，1=是）
        mindmap_data: 思维导图数据（JSON 对象）
        mindmap_url: 思维导图图片 URL
        tags: 标签列表
        status: 状态（draft/analyzing/completed/failed，默认 completed）
        knowledge_id: 关联知识库ID（可选）
        defect_id: 关联缺陷ID（可选）

    Returns:
        dict: 包含保存结果的字典
            - success: bool, 是否成功
            - defect_analysis_id: int, 缺陷分析 ID
            - analysis_name: str, 分析名称
            - message: str, 提示消息
            - error: str, 错误信息（如果失败）
    
    Examples:
        # 创建新缺陷分析
        result = await save_defect_analysis_tool(
            project_id=1,
            analysis_name="用户登录失败缺陷分析",
            defect_title="用户登录时出现500错误",
            executive_summary="分析用户登录功能出现的500错误...",
            root_cause_analysis={
                "primary_cause": "数据库连接超时",
                "contributing_factors": ["高并发", "连接池配置不当"]
            },
            severity="high",
            priority="urgent"
        )
        
        # 更新现有缺陷分析
        result = await save_defect_analysis_tool(
            project_id=1,
            defect_analysis_id=123,
            fix_status="fixed",
            fix_time_estimate="1 day"
        )
    """
    try:
        import json
        from module_testing.service.defect_analysis_service import DefectAnalysisService
        from config.get_db import get_db_session
        
        # 参数验证
        if not project_id:
            return {
                "success": False,
                "error": "project_id 是必填参数，请确保从上下文中获取",
                "message": "保存缺陷分析失败：缺少项目ID"
            }
        
        if not analysis_name and not defect_analysis_id:
            return {
                "success": False,
                "error": "创建新缺陷分析时，analysis_name 是必填参数",
                "message": "保存缺陷分析失败：缺少分析名称"
            }
        
        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 构建分析数据字典
        analysis_data = {
            "project_id": project_id,
            "analysis_name": analysis_name or f"缺陷分析_{defect_analysis_id}",
            "defect_title": defect_title,
            "defect_description": defect_description,
            "executive_summary": executive_summary,
            "severity": severity,
            "priority": priority,
            "defect_type": defect_type,
            "category": category,
            "affected_phase": affected_phase,
            "detection_phase": detection_phase,
            "root_cause_analysis": root_cause_analysis,
            "impact_analysis": impact_analysis,
            "reproduction_steps": reproduction_steps,
            "affected_modules": affected_modules,
            "fix_suggestions": fix_suggestions,
            "test_suggestions": test_suggestions,
            "prevention_measures": prevention_measures,
            "similar_defects": similar_defects,
            "use_rag": use_rag,
            "rag_context": rag_context,
            "mindmap_data": mindmap_data,
            "mindmap_url": mindmap_url,
            "status": status,
            "knowledge_id": knowledge_id,
            "defect_id": defect_id,
            "tags": tags,
            "fix_status": fix_status,
            "fix_time_estimate": fix_time_estimate,
        }
        
        # 移除 None 值
        analysis_data = {k: v for k, v in analysis_data.items() if v is not None}
        
        # 调用 Service 保存缺陷分析
        service = DefectAnalysisService()
        
        async with get_db_session() as db:
            if defect_analysis_id:
                # 更新现有缺陷分析
                result = await service.update_analysis(
                    db, defect_analysis_id, analysis_data, str(user_id)
                )
                if not result:
                    return {
                        "success": False,
                        "error": f"缺陷分析 {defect_analysis_id} 不存在",
                        "message": f"更新缺陷分析失败：缺陷分析 {defect_analysis_id} 不存在"
                    }
                
                logger.info(f"AI 成功更新缺陷分析: {defect_analysis_id} - {result.analysis_name}")
                
                return {
                    "success": True,
                    "defect_analysis_id": defect_analysis_id,
                    "analysis_name": result.analysis_name,
                    "message": f"✅ 缺陷分析 '{result.analysis_name}' (ID: {defect_analysis_id}) 更新成功"
                }
            else:
                # 创建新缺陷分析
                result = await service.create_analysis(
                    db, analysis_data, str(user_id)
                )
                logger.info(f"AI 成功创建缺陷分析: {result.analysis_id} - {result.analysis_name}")
                
                return {
                    "success": True,
                    "defect_analysis_id": result.analysis_id,
                    "analysis_name": result.analysis_name,
                    "message": f"✅ 缺陷分析 '{result.analysis_name}' (ID: {result.analysis_id}) 创建成功"
                }

    except Exception as e:
        logger.error(f"保存缺陷分析失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"保存缺陷分析失败: {str(e)}"
        }


# ============ 导入新工具 ============

# Human-in-the-Loop 工具
from module_testing.agents.human_in_the_loop import review_test_case_tool

# 文档解析工具
from module_testing.agents.document_parser import (
    parse_document_from_url
)


# ============ 思维导图生成工具 ============

@tool
async def generate_mindmap_tool(
    title: str,
    content: str,
    format: str = "markdown"
) -> Dict[str, Any]:
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
            - html: HTML 格式（通过 MCP 服务器生成）
        
    Returns:
        dict: 包含生成结果的字典
            - success: bool, 是否成功
            - mindmap_content: str, 思维导图内容
            - format: str, 输出格式
            - download_url: str, 下载链接（如果支持）
            - error: str, 错误信息（如果失败）
    """
    try:
        import os
        mindmap_mcp_url = _normalize_mcp_sse_url(
            os.environ.get("MINDMAP_MCP_URL", "http://localhost:9003/sse")
        )

        logger.info(f"开始生成思维导图: {title} (格式: {format})")

        from langchain_mcp_adapters.client import MultiServerMCPClient

        mcp_client = MultiServerMCPClient(
            {
                "mindmap": {
                    "url": mindmap_mcp_url,
                    "transport": "sse",
                }
            }
        )
        mcp_tools = list(await mcp_client.get_tools())
        tool = _pick_mcp_tool(mcp_tools, "generate_mindmap")
        
        if format == "markdown":
            # 如果 MCP 服务不可用，使用简单的 Markdown 格式
            if tool is None:
                logger.warning("未找到 MindMap MCP 工具（generate_mindmap），使用简单格式")
            
            mindmap = f"# {title}\n\n"
            lines = content.strip().split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped:
                    indent_level = (len(line) - len(stripped)) // 2
                    prefix = "  " * indent_level + "- "
                    mindmap += f"{prefix}{stripped}\n"
            
            return {
                "success": True,
                "mindmap_content": mindmap,
                "format": "markdown",
                "message": "思维导图生成成功（使用简单格式）"
            }
        else:
            # 非 markdown 格式需要 MCP 工具
            if tool is None:
                return {
                    "success": False,
                    "error": "未找到 MindMap MCP 工具（generate_mindmap）",
                    "message": "未找到 MindMap MCP 工具，请确保 MCP 服务已启动"
                }
            
            markdown = f"# {title}\n\n{content}"
            html = await tool.ainvoke(
                {
                    "markdown": markdown,
                    "return_type": "html",
                    "toolbar": True,
                }
            )
            
            return {
                "success": True,
                "mindmap_content": str(html),
                "format": "html",
                "download_url": None,
                "message": "思维导图生成成功",
            }
    
    except httpx.HTTPError as e:
        logger.error(f"MindMap 服务请求失败: {e}")
        return {
            "success": False,
            "error": f"MindMap 服务请求失败: {str(e)}",
            "message": f"MindMap 服务请求失败: {str(e)}"
        }
    except Exception as e:
        logger.error(f"思维导图生成失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"思维导图生成失败: {str(e)}",
            "message": f"思维导图生成失败: {str(e)}"
        }

