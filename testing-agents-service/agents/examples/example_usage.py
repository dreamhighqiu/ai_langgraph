"""
测试用例生成智能体使用示例

演示如何使用测试用例生成智能体来自动创建和更新测试用例
"""



import asyncio
from app.agents.testcase_generator import testcase_generator_agent, TestCaseGeneratorContext
from app.agents.tools import create_test_case_tool, update_test_case_tool


async def example_1_create_login_testcases():
    """示例 1: 为登录功能生成测试用例"""
    print("\n" + "="*60)
    print("示例 1: 为登录功能生成测试用例")
    print("="*60 + "\n")
    
    # 设置上下文
    context = TestCaseGeneratorContext(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        current_user_id="00000000-0000-0000-0000-000000000001"
    )
    
    # 用户需求
    user_input = """
    请为用户登录功能生成测试用例。
    
    功能描述：
    - 用户可以使用用户名和密码登录系统
    - 支持记住密码功能
    - 登录失败3次后锁定账号30分钟
    - 支持找回密码功能
    - 密码输入框支持显示/隐藏切换
    
    请生成包括正常流程、异常流程和边界条件的测试用例。
    """
    
    # 调用智能体
    result = await testcase_generator_agent.ainvoke({
        "messages": [{"role": "user", "content": user_input}],
        "context": context
    })
    
    print("智能体响应:")
    print(result)
# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TjFOVGFBPT06MzE3ZDY2OWI=


async def example_2_create_bdd_testcases():
    """示例 2: 使用 BDD 格式生成测试用例"""
    print("\n" + "="*60)
    print("示例 2: 使用 BDD 格式生成测试用例")
    print("="*60 + "\n")
    
    context = TestCaseGeneratorContext(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        template_type="test_case_bdd"
    )
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TjFOVGFBPT06MzE3ZDY2OWI=
    
    user_input = """
    请使用 BDD 格式为购物车功能生成测试用例。
    
    场景：
    1. 用户添加商品到购物车
       - 添加单个商品
       - 添加多个商品
       - 添加已存在的商品（数量累加）
    
    2. 用户修改购物车商品数量
       - 增加数量
       - 减少数量
       - 数量超过库存限制
    
    3. 用户删除购物车商品
       - 删除单个商品
       - 清空购物车
    """
    
    result = await testcase_generator_agent.ainvoke({
        "messages": [{"role": "user", "content": user_input}],
        "context": context
    })
    
    print("智能体响应:")
    print(result)


async def example_3_direct_tool_usage():
    """示例 3: 直接使用工具创建测试用例"""
    print("\n" + "="*60)
    print("示例 3: 直接使用工具创建测试用例")
    print("="*60 + "\n")
    
    # 创建普通测试用例
    result = await create_test_case_tool(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        name="用户使用正确凭据登录成功",
        description="验证用户输入正确的用户名和密码后能够成功登录系统",
        preconditions="用户已注册且账号状态正常",
        priority="critical",
        status="active",
        case_type="functional",
        test_case_steps=[
            {
                "step": "打开登录页面",
                "result": "页面正常显示，包含用户名和密码输入框"
            },
            {
                "step": "输入正确的用户名: testuser",
                "result": "用户名输入框接受输入"
            },
            {
                "step": "输入正确的密码: Test@123",
                "result": "密码输入框接受输入，显示为密文"
            },
            {
                "step": "点击登录按钮",
                "result": "系统验证通过，跳转到首页，显示欢迎信息"
            }
        ],
        tags=["登录", "核心功能", "正向测试"],
    )
    
    print("创建结果:")
    print(result)


async def example_4_create_bdd_tool():
    """示例 4: 直接使用工具创建 BDD 测试用例"""
    print("\n" + "="*60)
    print("示例 4: 直接使用工具创建 BDD 测试用例")
    print("="*60 + "\n")
    
    result = await create_test_case_tool(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        name="用户添加商品到购物车",
        description="验证用户能够成功将商品添加到购物车",
        template="test_case_bdd",
        priority="high",
        status="active",
        case_type="functional",
        feature="购物车管理",
        scenario="""
Scenario: 用户添加单个商品到购物车
  Given 用户已登录系统
  And 用户在商品详情页
  And 商品库存充足
  When 用户点击"加入购物车"按钮
  Then 商品成功添加到购物车
  And 购物车图标显示商品数量
  And 显示"添加成功"提示信息
        """,
        background="""
Background:
  Given 系统已启动
  And 数据库连接正常
        """,
        tags=["购物车", "BDD", "核心功能"],
    )
    
    print("创建结果:")
    print(result)


async def example_5_update_testcase():
    """示例 5: 更新测试用例"""
    print("\n" + "="*60)
    print("示例 5: 更新测试用例")
    print("="*60 + "\n")
    
    # 更新测试用例的优先级和状态
    result = await update_test_case_tool(
        project_identifier="PROJ-001",
        test_case_identifier="TC-1234",
        priority="critical",
        status="active",
        tags=["登录", "核心功能", "回归测试"],
    )
    
    print("更新结果:")
    print(result)
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TjFOVGFBPT06MzE3ZDY2OWI=


async def example_6_update_steps():
    """示例 6: 更新测试用例的步骤"""
    print("\n" + "="*60)
    print("示例 6: 更新测试用例的步骤")
    print("="*60 + "\n")
    
    result = await update_test_case_tool(
        project_identifier="PROJ-001",
        test_case_identifier="TC-1234",
        test_case_steps=[
            {
                "step": "打开登录页面",
                "result": "页面正常显示，包含用户名和密码输入框及验证码"
            },
            {
                "step": "输入正确的用户名和密码",
                "result": "输入框接受输入"
            },
            {
                "step": "输入正确的验证码",
                "result": "验证码输入框接受输入"
            },
            {
                "step": "点击登录按钮",
                "result": "系统验证通过，跳转到首页"
            }
        ],
    )
    
    print("更新结果:")
    print(result)
# type: ignore  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TjFOVGFBPT06MzE3ZDY2OWI=


async def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("测试用例生成智能体使用示例")
    print("="*60)
    
    # 注意: 以下示例需要实际的数据库连接和有效的项目/文件夹 ID
    # 在实际使用前，请确保：
    # 1. PostgreSQL 和 MongoDB 已启动
    # 2. 项目 PROJ-001 存在
    # 3. 文件夹 ID 有效
    # 4. DeepSeek API Key 已配置
    
    print("\n⚠️  注意: 这些示例需要实际的数据库连接")
    print("请确保数据库已启动并且配置正确\n")
    
    # 取消注释以运行示例
    # await example_1_create_login_testcases()
    # await example_2_create_bdd_testcases()
    # await example_3_direct_tool_usage()
    # await example_4_create_bdd_tool()
    # await example_5_update_testcase()
    # await example_6_update_steps()
    
    print("\n示例代码已准备就绪，请根据需要取消注释运行")


if __name__ == "__main__":
    asyncio.run(main())

