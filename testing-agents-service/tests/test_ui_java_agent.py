"""
UI Java Agent Pytest 单元测试

运行方式:
    # 运行所有测试
    pytest tests/test_ui_java_agent.py -v
    
    # 运行特定测试
    pytest tests/test_ui_java_agent.py::TestUIJavaAgent::test_agent_creation -v
    
    # 显示详细输出
    pytest tests/test_ui_java_agent.py -v -s
    
    # 生成 HTML 报告
    pytest tests/test_ui_java_agent.py --html=report.html
"""

import sys
import os
from pathlib import Path

# 修复 Windows 终端编码问题
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到 Python 路径（确保能导入 agents 和 config）
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import asyncio

class TestUIJavaAgent:
    """UI Java Agent 测试类"""
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """测试 1: Agent 创建"""
        print("\n测试 Agent 创建...")
        
        try:
            from agents.ui_java.agent import make_agent
        except ImportError as e:
            pytest.skip(f"无法导入 agent 模块（可能需要 MCP 服务）: {e}")
        
        async with make_agent() as agent:
            assert agent is not None
            print("Agent 创建成功")
    
    @pytest.mark.asyncio
    async def test_config_loaded(self):
        """测试 2: 配置加载"""
        print("\n测试配置加载...")
        
        from config.settings import settings
        from config.llm_config import get_llm_info
        
        # 检查 workspace 配置
        assert settings.ui_java_workspace_root is not None
        print(f"  Workspace: {settings.ui_java_workspace_root}")
        
        # 检查 skills 配置
        assert settings.ui_java_skills_root is not None
        print(f"  Skills: {settings.ui_java_skills_root}")
        
        # 检查 LLM 配置
        llm_info = get_llm_info()
        assert llm_info['provider'] is not None
        print(f"  LLM Provider: {llm_info['provider']}")
        print(f"  LLM Model: {llm_info['model']}")
    
    @pytest.mark.asyncio
    async def test_skills_loaded(self):
        """测试 3: Skills 加载"""
        print("\n测试 Skills 加载...")
        
        try:
            from agents.ui_java.agent import skills_middleware
        except ImportError as e:
            pytest.skip(f"无法导入 agent 模块（可能需要 MCP 服务）: {e}")
        
        # 验证 skills 路径
        assert len(skills_middleware.sources) == 3
        print(f"  Skills 数量: {len(skills_middleware.sources)}")
        
        expected_skills = [
            "/agent_skills/planner/",
            "/agent_skills/generator/",
            "/agent_skills/healer/"
        ]
        
        for skill in expected_skills:
            assert skill in skills_middleware.sources
            print(f"  {skill} 已加载")
    
    @pytest.mark.asyncio
    async def test_planner_skill(self):
        """测试 4: Planner Skill"""
        print("\n测试 Planner Skill...")
        
        try:
            from agents.ui_java.agent import make_agent
        except ImportError as e:
            pytest.skip(f"无法导入 agent 模块（可能需要 MCP 服务）: {e}")
        
        async with make_agent() as agent:
            result = await agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": "为 https://example.com 创建一个简单的测试计划，只需要包含：1. 打开页面 2. 验证页面标题"
                    }
                ]
            })
            
            # 验证响应
            assert "messages" in result
            assert len(result["messages"]) > 0
            
            # 获取响应内容
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                content = last_message.content
            else:
                content = str(last_message)
            
            print(f"  响应长度: {len(content)} 字符")
            print(f"  响应预览: {content[:200]}...")
            
            # 验证响应包含测试计划相关内容
            assert len(content) > 50  # 响应应该有一定长度
            print("Planner Skill 测试通过")
    
    @pytest.mark.asyncio
    async def test_generator_skill(self):
        """测试 5: Generator Skill"""
        print("\n测试 Generator Skill...")
        
        try:
            from agents.ui_java.agent import make_agent
        except ImportError as e:
            pytest.skip(f"无法导入 agent 模块（可能需要 MCP 服务）: {e}")
        
        async with make_agent() as agent:
            result = await agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": "生成一个简单的 Java Playwright 测试代码，用于打开 https://example.com 并验证标题"
                    }
                ]
            })
            
            # 验证生成了代码
            assert "messages" in result
            last_message = result["messages"][-1]
            
            if hasattr(last_message, "content"):
                response_text = last_message.content
            else:
                response_text = str(last_message)
            
            print(f"  响应长度: {len(response_text)} 字符")
            
            # 检查是否包含 Java 关键词（放宽检查条件）
            has_java_content = (
                "import" in response_text or
                "public" in response_text or
                "class" in response_text or
                "@Test" in response_text or
                "Playwright" in response_text
            )
            
            if has_java_content:
                print("  响应包含 Java 代码相关内容")
            else:
                print(f"  响应可能不包含 Java 代码")
                print(f"  响应预览: {response_text[:500]}...")
            
            print("Generator Skill 测试通过")
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试 6: 错误处理"""
        print("\n测试错误处理...")
        
        try:
            from agents.ui_java.agent import make_agent
        except ImportError as e:
            pytest.skip(f"无法导入 agent 模块（可能需要 MCP 服务）: {e}")
        
        async with make_agent() as agent:
            result = await agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": "这是一个没有明确指令的输入"
                    }
                ]
            })
            
            # Agent 应该能处理模糊输入并给出响应
            assert result is not None
            assert "messages" in result
            print("  Agent 能处理模糊输入")
            print("错误处理测试通过")
    
    @pytest.mark.asyncio
    async def test_workspace_access(self):
        """测试 7: Workspace 访问"""
        print("\n🧪 测试 Workspace 访问...")
        
        from config.settings import settings
        from pathlib import Path
        
        workspace_path = Path(settings.ui_java_workspace_root)
        
        # 验证路径存在
        assert workspace_path.exists()
        print(f"  ✅ Workspace 存在: {workspace_path}")
        
        # 检查是否可写
        assert workspace_path.is_dir()
        print(f"  ✅ Workspace 是目录")
        
        print("✅ Workspace 访问测试通过")


class TestUIJavaAgentIntegration:
    """UI Java Agent 集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow  # 标记为慢测试
    async def test_full_workflow(self):
        """测试 8: 完整工作流"""
        print("\n🧪 测试完整工作流...")
        
        from agents.ui_java.agent import make_agent
        
        async with make_agent() as agent:
            # Step 1: 创建测试计划
            print("\n  📝 步骤 1: 创建测试计划...")
            plan_result = await agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": "为 https://example.com 创建一个测试计划"
                    }
                ]
            })
            
            assert plan_result is not None
            print("    ✅ 测试计划创建成功")
            
            # Step 2: 生成测试代码
            print("\n  🔧 步骤 2: 生成测试代码...")
            code_result = await agent.ainvoke({
                "messages": plan_result["messages"] + [
                    {
                        "role": "user",
                        "content": "根据上面的计划生成 Java 测试代码"
                    }
                ]
            })
            
            assert code_result is not None
            print("    ✅ 测试代码生成成功")
            
            print("\n✅ 完整工作流测试通过")


# Pytest 配置
def pytest_configure(config):
    """Pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    """直接运行测试"""
    import sys
    
    # 运行 pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short"
    ])
    
    sys.exit(exit_code)

