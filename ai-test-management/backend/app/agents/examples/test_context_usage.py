"""
测试智能体上下文参数使用

验证智能体是否正确使用前端传入的上下文参数
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import asyncio
from app.agents.testcase_generator import testcase_generator_agent, TestCaseGeneratorContext


async def test_context_usage_normal():
    """测试场景 1: 普通测试用例 - 验证智能体使用正确的上下文参数"""
    print("\n" + "="*80)
    print("测试场景 1: 普通测试用例 - 验证上下文参数使用")
    print("="*80 + "\n")
    
    # 设置上下文
    context = TestCaseGeneratorContext(
        project_identifier="PROJ-TEST-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        template_type="test_case"
    )
    
    print(f"📋 上下文信息:")
    print(f"   项目标识符: {context.project_identifier}")
    print(f"   文件夹 ID: {context.folder_id}")
    print(f"   模板类型: {context.template_type}")
    print()
    
    # 用户输入
    user_input = "为用户登录功能生成一个测试用例，验证正确凭据登录成功的场景"
    
    print(f"💬 用户输入: {user_input}\n")
    print("🤖 智能体处理中...\n")
# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1cxeFF3PT06Mzk2YzU5NGE=
    
    # 调用智能体
    try:
        result = await testcase_generator_agent.ainvoke({
            "messages": [{"role": "user", "content": user_input}],
            "context": context
        })
        
        print("✅ 智能体响应:")
        print(result)
        print("\n" + "="*80)
        print("验证点:")
        print("1. 智能体是否使用了 project_identifier='PROJ-TEST-001'?")
        print("2. 智能体是否使用了指定的 folder_id?")
        print("3. 智能体是否创建了普通格式的测试用例（test_case_steps）?")
        print("4. 智能体是否没有询问用户提供项目或文件夹信息?")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}\n")


async def test_context_usage_bdd():
    """测试场景 2: BDD 测试用例 - 验证模板类型选择"""
    print("\n" + "="*80)
    print("测试场景 2: BDD 测试用例 - 验证模板类型选择")
    print("="*80 + "\n")
    
    # 设置上下文
    context = TestCaseGeneratorContext(
        project_identifier="PROJ-TEST-002",
        folder_id="223e4567-e89b-12d3-a456-426614174000",
        template_type="test_case_bdd"
    )
    
    print(f"📋 上下文信息:")
    print(f"   项目标识符: {context.project_identifier}")
    print(f"   文件夹 ID: {context.folder_id}")
    print(f"   模板类型: {context.template_type}")
    print()
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1cxeFF3PT06Mzk2YzU5NGE=
    
    # 用户输入
    user_input = "为购物车添加商品功能生成一个测试用例"
    
    print(f"💬 用户输入: {user_input}\n")
    print("🤖 智能体处理中...\n")
    
    # 调用智能体
    try:
        result = await testcase_generator_agent.ainvoke({
            "messages": [{"role": "user", "content": user_input}],
            "context": context
        })
        
        print("✅ 智能体响应:")
        print(result)
        print("\n" + "="*80)
        print("验证点:")
        print("1. 智能体是否使用了 project_identifier='PROJ-TEST-002'?")
        print("2. 智能体是否使用了指定的 folder_id?")
        print("3. 智能体是否创建了 BDD 格式的测试用例（feature/scenario）?")
        print("4. 智能体是否使用了 template='test_case_bdd'?")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}\n")


async def test_context_empty_params():
    """测试场景 3: 空参数 - 验证错误处理"""
    print("\n" + "="*80)
    print("测试场景 3: 空参数 - 验证错误处理")
    print("="*80 + "\n")
    
    # 设置上下文（参数为空）
    context = TestCaseGeneratorContext(
        project_identifier="",
        folder_id="",
        template_type="test_case"
    )
    
    print(f"📋 上下文信息:")
    print(f"   项目标识符: '{context.project_identifier}' (空)")
    print(f"   文件夹 ID: '{context.folder_id}' (空)")
    print(f"   模板类型: {context.template_type}")
    print()
    
    # 用户输入
    user_input = "生成一个测试用例"
    
    print(f"💬 用户输入: {user_input}\n")
    print("🤖 智能体处理中...\n")
    
    # 调用智能体
    try:
        result = await testcase_generator_agent.ainvoke({
            "messages": [{"role": "user", "content": user_input}],
            "context": context
        })
        
        print("✅ 智能体响应:")
        print(result)
        print("\n" + "="*80)
        print("验证点:")
        print("1. 智能体是否提示了'系统配置错误'或类似的错误信息?")
        print("2. 智能体是否没有尝试创建测试用例?")
        print("3. 智能体是否给出了明确的解决建议?")
        print("="*80 + "\n")
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1cxeFF3PT06Mzk2YzU5NGE=
        
    except Exception as e:
        print(f"❌ 错误: {e}\n")


async def test_prompt_content():
    """测试场景 4: 查看生成的提示词内容"""
    print("\n" + "="*80)
    print("测试场景 4: 查看生成的提示词内容")
    print("="*80 + "\n")
    
    from app.agents.testcase_generator import dynamic_prompt_fn
    from langchain.agents.middleware import ModelRequest
    from unittest.mock import Mock
    
    # 创建模拟的 request 对象
    mock_request = Mock(spec=ModelRequest)
    mock_context = TestCaseGeneratorContext(
        project_identifier="PROJ-DEMO",
        folder_id="demo-folder-uuid",
        template_type="test_case"
    )
    mock_request.runtime.context = mock_context
    
    # 生成提示词
    prompt = dynamic_prompt_fn(mock_request)
    
    print("📝 生成的系统提示词（前 2000 字符）:\n")
    print(prompt[:2000])
    print("\n...")
    print("\n" + "="*80)
    print("验证点:")
    print("1. 提示词中是否包含 '当前上下文信息' 部分?")
    print("2. 提示词中是否显示了 project_identifier='PROJ-DEMO'?")
    print("3. 提示词中是否显示了 folder_id='demo-folder-uuid'?")
    print("4. 提示词中是否包含正确和错误的调用示例?")
    print("="*80 + "\n")

# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1cxeFF3PT06Mzk2YzU5NGE=

async def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("智能体上下文参数使用测试")
    print("="*80)
    
    print("\n⚠️  注意:")
    print("- 测试场景 1 和 2 需要实际的数据库连接")
    print("- 测试场景 3 用于验证错误处理")
    print("- 测试场景 4 只查看提示词内容，不需要数据库")
    print()
    
    # 测试场景 4 - 查看提示词（不需要数据库）
    await test_prompt_content()
    
    # 以下测试需要数据库连接，取消注释以运行
    # await test_context_usage_normal()
    # await test_context_usage_bdd()
    # await test_context_empty_params()
    
    print("\n✅ 测试完成！")
    print("\n💡 提示:")
    print("- 取消注释 main() 中的测试函数以运行完整测试")
    print("- 确保数据库连接正常后再运行测试场景 1-3")


if __name__ == "__main__":
    asyncio.run(main())

