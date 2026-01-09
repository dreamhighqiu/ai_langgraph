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
        folder_id: 文件夹ID（可选，从上下文自动获取）
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
        # 直接调用 Service 层，绕过 HTTP 认证
        from module_testing.service.test_case_service import TestCaseService
        from module_testing.entity.vo.test_case_vo import TestCaseCreateVO
        from config.get_db import get_db_session
        
        # 构建 VO 对象
        test_case_vo = TestCaseCreateVO(
            case_name=name,
            project_id=project_id,
            folder_id=folder_id,
            description=description,
            module=module,
            case_type=case_type,
            priority=priority,
            status=status,
            preconditions=preconditions,
            expected_result=expected_result,
            test_data=test_data,
            tags=tags,
            template=template,
        )
        
        # 根据模板类型添加相应字段
        if template == "test_case_bdd":
            if feature:
                test_case_vo.feature = feature
            if scenario:
                test_case_vo.scenario = scenario
            if background:
                test_case_vo.background = background
        else:
            if test_case_steps:
                test_case_vo.test_case_steps = test_case_steps
        
        # 调用 Service 创建测试用例
        service = TestCaseService()
        
        async with get_db_session() as db:
            result = await service.create_test_case(
                db, test_case_vo, "ai_agent"  # 使用 ai_agent 作为创建者
            )
            
            return {
                "success": True,
                "data": {
                    "case_id": result.case_id,
                    "case_identifier": result.case_identifier,
                    "case_name": result.case_name,
                },
                "message": f"测试用例 '{name}' (ID: {result.case_id}) 创建成功"
            }

    except Exception as e:
        logger.error(f"创建测试用例失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": f"创建测试用例失败: {str(e)}"
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
        test_cases: 测试用例列表，每个元素包含以下字段：
            - name: 测试用例名称（必填）
            - description: 测试用例描述（可选）
            - preconditions: 前置条件（可选）
            - priority: 优先级（可选，默认 medium）
            - case_type: 测试类型（可选，默认 functional）
            - test_case_steps: 测试步骤列表（可选）
            - tags: 标签列表（可选）
            - template: 模板类型（可选，默认 test_case）
            - feature: BDD Feature（可选）
            - scenario: BDD Scenario（可选）
        folder_id: 文件夹ID（可选，从上下文自动获取）

    Returns:
        dict: 包含批量创建结果的字典
            - success: bool, 是否成功
            - data: 包含成功和失败的统计信息
                - total: 总数
                - succeeded: 成功数量
                - failed: 失败数量
                - results: 每个测试用例的创建结果

    Examples:
        result = await batch_create_test_cases_tool(
            project_id=1,
            folder_id=10,
            test_cases=[
                {
                    "name": "测试用例1",
                    "description": "描述1",
                    "priority": "high",
                    "test_case_steps": [
                        {"step": "步骤1", "expected": "结果1"}
                    ]
                },
                {
                    "name": "测试用例2",
                    "description": "描述2",
                    "priority": "medium",
                    "test_case_steps": [
                        {"step": "步骤1", "expected": "结果1"}
                    ]
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
        from module_testing.entity.vo.test_case_vo import TestCaseCreateVO
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
                        expected_result=tc.get("expected_result"),
                        test_data=tc.get("test_data"),
                        tags=tc.get("tags"),
                        template=tc.get("template", "test_case"),
                        test_case_steps=tc.get("test_case_steps"),
                        feature=tc.get("feature"),
                        scenario=tc.get("scenario"),
                        background=tc.get("background"),
                    )
                    
                    # 调用 Service 创建
                    result = await service.create_test_case(
                        db, test_case_vo, "ai_agent"
                    )
                    
                    results.append({
                        "index": index,
                        "name": name,
                        "success": True,
                        "data": {
                            "case_id": result.case_id,
                            "case_identifier": result.case_identifier,
                        },
                        "message": f"测试用例 '{name}' 创建成功"
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
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    RAG 知识库检索工具

    从知识库检索相关的上下文信息，帮助生成更准确的测试用例。

    Args:
        query: 查询描述
        top_k: 返回的结果数量

    Returns:
        dict: 包含检索结果的字典
    """
    try:
        # 构建 API URL
        url = get_api_url("/api/testing/knowledge/query")

        # 发送 HTTP POST 请求
        response_data = await make_http_request(
            method="POST",
            url=url,
            json_data={
                "query": query,
                "top_k": top_k
            },
        )

        return {
            "success": True,
            "data": response_data.get("data"),
            "context": response_data.get("data", {}).get("context", ""),
            "message": "RAG 检索成功"
        }

    except Exception as e:
        logger.error(f"RAG 检索失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"RAG 检索失败: {str(e)}",
            "context": ""
        }


@tool
async def save_requirement_analysis_tool(
    project_id: int,
    title: str,
    executive_summary: str,
    functional_requirements: str,
    non_functional_requirements: Optional[str] = None,
    user_stories: Optional[str] = None,
    acceptance_criteria: Optional[str] = None,
    constraints: Optional[str] = None,
    module: Optional[str] = None,
) -> Dict[str, Any]:
    """
    保存需求分析工具

    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        title: 需求分析标题
        executive_summary: 需求概述
        functional_requirements: 功能需求
        non_functional_requirements: 非功能需求
        user_stories: 用户故事
        acceptance_criteria: 验收标准
        constraints: 约束条件
        module: 所属模块

    Returns:
        dict: 包含保存结果的字典
    """
    try:
        # 构建请求数据
        request_data = {
            "project_id": project_id,
            "title": title,
            "executive_summary": executive_summary,
            "functional_requirements": functional_requirements,
        }

        # 添加可选字段
        if non_functional_requirements:
            request_data["non_functional_requirements"] = non_functional_requirements
        if user_stories:
            request_data["user_stories"] = user_stories
        if acceptance_criteria:
            request_data["acceptance_criteria"] = acceptance_criteria
        if constraints:
            request_data["constraints"] = constraints
        if module:
            request_data["module"] = module

        # 构建 API URL
        url = get_api_url("/api/testing/requirement-analyses")

        # 发送 HTTP POST 请求
        response_data = await make_http_request(
            method="POST",
            url=url,
            json_data=request_data,
        )

        return {
            "success": True,
            "data": response_data.get("data"),
            "message": f"需求分析 {response_data.get('data', {}).get('id')} 保存成功"
        }

    except Exception as e:
        logger.error(f"保存需求分析失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"保存需求分析失败: {str(e)}"
        }


@tool
async def save_defect_analysis_tool(
    project_id: int,
    title: str,
    executive_summary: str,
    root_cause_analysis: str,
    impact_analysis: str,
    reproduction_steps: Optional[str] = None,
    affected_modules: Optional[str] = None,
    fix_recommendations: Optional[str] = None,
    testing_suggestions: Optional[str] = None,
    prevention_measures: Optional[str] = None,
    priority: str = "medium",
    severity: str = "medium",
) -> Dict[str, Any]:
    """
    保存缺陷分析工具

    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        title: 缺陷分析标题
        executive_summary: 缺陷概述
        root_cause_analysis: 根本原因分析
        impact_analysis: 影响分析
        reproduction_steps: 复现步骤
        affected_modules: 受影响模块
        fix_recommendations: 修复建议
        testing_suggestions: 测试建议
        prevention_measures: 预防措施
        priority: 优先级
        severity: 严重程度

    Returns:
        dict: 包含保存结果的字典
    """
    try:
        # 构建请求数据
        request_data = {
            "project_id": project_id,
            "title": title,
            "executive_summary": executive_summary,
            "root_cause_analysis": root_cause_analysis,
            "impact_analysis": impact_analysis,
            "priority": priority,
            "severity": severity,
        }

        # 添加可选字段
        if reproduction_steps:
            request_data["reproduction_steps"] = reproduction_steps
        if affected_modules:
            request_data["affected_modules"] = affected_modules
        if fix_recommendations:
            request_data["fix_recommendations"] = fix_recommendations
        if testing_suggestions:
            request_data["testing_suggestions"] = testing_suggestions
        if prevention_measures:
            request_data["prevention_measures"] = prevention_measures

        # 构建 API URL
        url = get_api_url("/api/testing/defect-analyses")

        # 发送 HTTP POST 请求
        response_data = await make_http_request(
            method="POST",
            url=url,
            json_data=request_data,
        )

        return {
            "success": True,
            "data": response_data.get("data"),
            "message": f"缺陷分析 {response_data.get('data', {}).get('id')} 保存成功"
        }

    except Exception as e:
        logger.error(f"保存缺陷分析失败: {str(e)}")
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
    parse_document_from_url,
    parse_document_content
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
    
    将测试用例或需求内容转换为思维导图格式。
    
    Args:
        title: 思维导图标题
        content: 要转换的内容（测试用例、需求等）
        format: 输出格式（markdown, mermaid, xmind）
        
    Returns:
        dict: 包含生成结果的字典
            - success: bool, 是否成功
            - mindmap_content: str, 思维导图内容
            - format: str, 输出格式
    """
    try:
        if format == "markdown":
            # 生成 Markdown 格式的思维导图
            mindmap = f"# {title}\n\n"
            
            # 解析内容生成树状结构
            lines = content.strip().split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped:
                    # 根据缩进生成层级
                    indent_level = (len(line) - len(stripped)) // 2
                    prefix = "  " * indent_level + "- "
                    mindmap += f"{prefix}{stripped}\n"
            
            return {
                "success": True,
                "mindmap_content": mindmap,
                "format": "markdown",
                "message": "思维导图生成成功"
            }
        
        elif format == "mermaid":
            # 生成 Mermaid 格式
            mermaid = f"mindmap\n  root(({title}))\n"
            
            lines = content.strip().split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped:
                    indent_level = (len(line) - len(stripped)) // 2 + 2
                    indent = "  " * indent_level
                    mermaid += f"{indent}{stripped}\n"
            
            return {
                "success": True,
                "mindmap_content": mermaid,
                "format": "mermaid",
                "message": "思维导图生成成功"
            }
        
        else:
            return {
                "success": False,
                "error": f"不支持的格式: {format}",
                "message": f"不支持的格式: {format}。支持: markdown, mermaid"
            }
            
    except Exception as e:
        logger.error(f"生成思维导图失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"生成思维导图失败: {str(e)}"
        }

