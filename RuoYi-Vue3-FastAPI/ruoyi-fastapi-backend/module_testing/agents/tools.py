"""
智能体工具集

提供测试用例创建、RAG检索等工具函数，供智能体调用
通过 HTTP 接口调用，降低耦合度

架构参考: ai-test-management 项目
"""

import httpx
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool

from config.env import AppConfig
from utils.log_util import logger


# ============ 配置 ============

# API 基础 URL
API_BASE_URL = f"http://{AppConfig.app_host}:{AppConfig.app_port}"
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
) -> dict:
    """
    发送 HTTP 请求的通用函数
    
    Args:
        method: HTTP 方法（GET, POST, PATCH, DELETE）
        url: 完整的 URL
        json_data: JSON 请求体
        params: URL 查询参数
        timeout: 超时时间（秒）
        
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
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", error_detail)
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
    description: Optional[str] = None,
    module: Optional[str] = None,
    test_type: str = "functional",
    priority: str = "medium",
    preconditions: Optional[str] = None,
    test_steps: Optional[str] = None,
    expected_results: Optional[str] = None,
    test_data: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    创建测试用例工具（通过 HTTP 接口调用）
    
    该工具通过调用测试用例创建 HTTP 接口来创建新的测试用例。
    
    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        name: 测试用例名称（必填）
        description: 测试用例描述
        module: 所属模块
        test_type: 测试类型（functional, performance, security等）
        priority: 优先级（high, medium, low）
        preconditions: 前置条件
        test_steps: 测试步骤
        expected_results: 预期结果
        test_data: 测试数据
        tags: 标签列表
        
    Returns:
        dict: 包含创建结果的字典
            - success: 是否成功
            - data: 创建的测试用例信息（如果成功）
            - error: 错误信息（如果失败）
    """
    try:
        # 构建请求数据
        request_data = {
            "name": name,
            "project_id": project_id,
            "test_type": test_type,
            "priority": priority,
        }
        
        # 添加可选字段
        if description:
            request_data["description"] = description
        if module:
            request_data["module"] = module
        if preconditions:
            request_data["preconditions"] = preconditions
        if test_steps:
            request_data["test_steps"] = test_steps
        if expected_results:
            request_data["expected_results"] = expected_results
        if test_data:
            request_data["test_data"] = test_data
        if tags:
            request_data["tags"] = tags
        
        # 构建 API URL
        url = get_api_url("/api/testing/test-cases")
        
        # 发送 HTTP POST 请求
        response_data = await make_http_request(
            method="POST",
            url=url,
            json_data=request_data,
        )
        
        return {
            "success": True,
            "data": response_data.get("data"),
            "message": f"测试用例 {response_data.get('data', {}).get('id')} 创建成功"
        }

    except Exception as e:
        logger.error(f"创建测试用例失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"创建测试用例失败: {str(e)}"
        }


@tool
async def update_test_case_tool(
    test_case_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    module: Optional[str] = None,
    test_type: Optional[str] = None,
    priority: Optional[str] = None,
    preconditions: Optional[str] = None,
    test_steps: Optional[str] = None,
    expected_results: Optional[str] = None,
    test_data: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    更新测试用例工具

    Args:
        test_case_id: 测试用例ID（必填）
        其他参数同 create_test_case_tool，均为可选

    Returns:
        dict: 包含更新结果的字典
    """
    try:
        # 构建请求数据，只包含非 None 的字段
        request_data = {}

        if name is not None:
            request_data["name"] = name
        if description is not None:
            request_data["description"] = description
        if module is not None:
            request_data["module"] = module
        if test_type is not None:
            request_data["test_type"] = test_type
        if priority is not None:
            request_data["priority"] = priority
        if preconditions is not None:
            request_data["preconditions"] = preconditions
        if test_steps is not None:
            request_data["test_steps"] = test_steps
        if expected_results is not None:
            request_data["expected_results"] = expected_results
        if test_data is not None:
            request_data["test_data"] = test_data
        if tags is not None:
            request_data["tags"] = tags

        # 构建 API URL
        url = get_api_url(f"/api/testing/test-cases/{test_case_id}")

        # 发送 HTTP PATCH 请求
        response_data = await make_http_request(
            method="PATCH",
            url=url,
            json_data=request_data,
        )

        return {
            "success": True,
            "data": response_data.get("data"),
            "message": f"测试用例 {test_case_id} 更新成功"
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
) -> Dict[str, Any]:
    """
    批量创建测试用例工具

    Args:
        project_id: 项目ID（必填，从上下文自动获取）
        test_cases: 测试用例列表，每个元素是一个测试用例字典

    Returns:
        dict: 包含创建结果的字典
    """
    try:
        # 为每个测试用例添加 project_id
        for tc in test_cases:
            tc["project_id"] = project_id

        # 构建 API URL
        url = get_api_url("/api/testing/test-cases/batch")

        # 发送 HTTP POST 请求
        response_data = await make_http_request(
            method="POST",
            url=url,
            json_data={"test_cases": test_cases},
        )

        created_count = len(response_data.get("data", []))

        return {
            "success": True,
            "data": response_data.get("data"),
            "message": f"成功批量创建 {created_count} 个测试用例"
        }

    except Exception as e:
        logger.error(f"批量创建测试用例失败: {str(e)}")
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

