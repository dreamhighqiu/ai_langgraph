"""
测试用例生成工具的单元测试

用于验证工具函数的正确性
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import UUID

from app.agents.tools import create_test_case_tool, update_test_case_tool
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVdRMmFnPT06YjkxZTFjOWE=


class TestCreateTestCaseTool:
    """测试创建测试用例工具"""
    
    @pytest.mark.asyncio
    async def test_create_normal_testcase(self):
        """测试创建普通测试用例"""
        # 模拟数据库会话和服务
        with patch('app.agents.tools.async_session_factory') as mock_session_factory, \
             patch('app.agents.tools.MongoDB') as mock_mongodb:
            
            # 设置模拟对象
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            mock_mongodb.get_database.return_value = Mock()
            
            # 模拟服务返回值
            mock_test_case = Mock()
            mock_test_case.id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_test_case.identifier = "TC-001"
            mock_test_case.name = "测试用例"
            mock_test_case.description = "描述"
            mock_test_case.priority = "high"
            mock_test_case.status = "active"
            mock_test_case.case_type = "functional"
            mock_test_case.template = "test_case"
            mock_test_case.created_at = None
            
            with patch('app.agents.tools.TestCaseService') as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.create_test_case.return_value = mock_test_case
                
                # 调用工具
                result = await create_test_case_tool(
                    project_identifier="PROJ-001",
                    folder_id="123e4567-e89b-12d3-a456-426614174000",
                    name="测试用例",
                    description="描述",
                    priority="high",
                    status="active",
                    case_type="functional",
                    test_case_steps=[
                        {"step": "步骤1", "result": "结果1"},
                        {"step": "步骤2", "result": "结果2"}
                    ]
                )
                
                # 验证结果
                assert result["success"] is True
                assert result["data"]["identifier"] == "TC-001"
                assert result["data"]["name"] == "测试用例"
    
    @pytest.mark.asyncio
    async def test_create_bdd_testcase(self):
        """测试创建 BDD 测试用例"""
        with patch('app.agents.tools.async_session_factory') as mock_session_factory, \
             patch('app.agents.tools.MongoDB') as mock_mongodb:
            
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            mock_mongodb.get_database.return_value = Mock()
            
            mock_test_case = Mock()
            mock_test_case.id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_test_case.identifier = "TC-002"
            mock_test_case.name = "BDD 测试用例"
            mock_test_case.description = "BDD 描述"
            mock_test_case.priority = "medium"
            mock_test_case.status = "draft"
            mock_test_case.case_type = "functional"
            mock_test_case.template = "test_case_bdd"
            mock_test_case.created_at = None
            
            with patch('app.agents.tools.TestCaseService') as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.create_test_case.return_value = mock_test_case
                
                result = await create_test_case_tool(
                    project_identifier="PROJ-001",
                    folder_id="123e4567-e89b-12d3-a456-426614174000",
                    name="BDD 测试用例",
                    template="test_case_bdd",
                    feature="用户认证",
                    scenario="用户登录",
                    background="Given 用户已注册"
                )
                
                assert result["success"] is True
                assert result["data"]["identifier"] == "TC-002"
    
    @pytest.mark.asyncio
    async def test_create_testcase_error(self):
        """测试创建测试用例时的错误处理"""
        with patch('app.agents.tools.async_session_factory') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVdRMmFnPT06YjkxZTFjOWE=
            
            with patch('app.agents.tools.TestCaseService') as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.create_test_case.side_effect = Exception("数据库错误")
                
                result = await create_test_case_tool(
                    project_identifier="PROJ-001",
                    folder_id="123e4567-e89b-12d3-a456-426614174000",
                    name="测试用例"
                )
                
                assert result["success"] is False
                assert "error" in result
                assert "数据库错误" in result["error"]


class TestUpdateTestCaseTool:
    """测试更新测试用例工具"""
    
    @pytest.mark.asyncio
    async def test_update_testcase(self):
        """测试更新测试用例"""
        with patch('app.agents.tools.async_session_factory') as mock_session_factory, \
             patch('app.agents.tools.MongoDB') as mock_mongodb:
            
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__.return_value = mock_session
            mock_mongodb.get_database.return_value = Mock()
            
            mock_test_case = Mock()
            mock_test_case.id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_test_case.identifier = "TC-001"
            mock_test_case.name = "更新后的名称"
            mock_test_case.description = "更新后的描述"
            mock_test_case.priority = "critical"
            mock_test_case.status = "active"
            mock_test_case.case_type = "regression"
            mock_test_case.version = 2
            mock_test_case.updated_at = None
            
            with patch('app.agents.tools.TestCaseService') as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.update_test_case.return_value = mock_test_case
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVdRMmFnPT06YjkxZTFjOWE=
                
                result = await update_test_case_tool(
                    project_identifier="PROJ-001",
                    test_case_identifier="TC-001",
                    name="更新后的名称",
                    priority="critical",
                    status="active"
                )
                
                assert result["success"] is True
                assert result["data"]["identifier"] == "TC-001"
                assert result["data"]["name"] == "更新后的名称"
                assert result["data"]["version"] == 2
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVdRMmFnPT06YjkxZTFjOWE=


# 简单的手动测试函数
async def manual_test():
    """手动测试函数（需要实际数据库连接）"""
    print("开始手动测试...")
    print("注意: 此测试需要实际的数据库连接")
    
    # 测试创建普通测试用例
    print("\n1. 测试创建普通测试用例...")
    result = await create_test_case_tool(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        name="手动测试用例",
        description="这是一个手动测试用例",
        priority="medium",
        status="draft",
        case_type="functional",
        test_case_steps=[
            {"step": "步骤1", "result": "预期结果1"},
            {"step": "步骤2", "result": "预期结果2"}
        ],
        tags=["测试", "手动"]
    )
    print(f"结果: {result}")
    
    # 如果创建成功，测试更新
    if result.get("success"):
        test_case_id = result["data"]["identifier"]
        print(f"\n2. 测试更新测试用例 {test_case_id}...")
        update_result = await update_test_case_tool(
            project_identifier="PROJ-001",
            test_case_identifier=test_case_id,
            priority="high",
            status="active"
        )
        print(f"结果: {update_result}")


if __name__ == "__main__":
    print("运行单元测试: pytest backend/app/agents/test_tools.py")
    print("\n或运行手动测试（需要数据库）:")
    # asyncio.run(manual_test())

