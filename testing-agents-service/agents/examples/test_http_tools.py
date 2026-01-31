"""
测试 HTTP 工具函数

测试通过 HTTP 接口调用的测试用例工具
"""



import asyncio
from tools import create_test_case_tool, update_test_case_tool, batch_create_test_cases_tool


async def test_create_test_case():
    """测试创建单个测试用例"""
    print("\n" + "="*60)
    print("测试 1: 创建单个测试用例")
    print("="*60)
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U1ZKYVdnPT06MTc4YWFlYjk=
    
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
    
    print(f"结果: {result}")
    return result


async def test_create_bdd_test_case():
    """测试创建 BDD 测试用例"""
    print("\n" + "="*60)
    print("测试 2: 创建 BDD 测试用例")
    print("="*60)
    
    result = await create_test_case_tool(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        name="用户登录场景",
        template="test_case_bdd",
        feature="用户认证",
        scenario="用户使用正确的凭据登录",
        background="Given 用户已注册"
    )
    
    print(f"结果: {result}")
    return result


async def test_update_test_case():
    """测试更新测试用例"""
    print("\n" + "="*60)
    print("测试 3: 更新测试用例")
    print("="*60)
    
    result = await update_test_case_tool(
        project_identifier="PROJ-001",
        test_case_identifier="TC-1234",
        priority="critical",
        status="active",
        description="更新后的描述"
    )
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U1ZKYVdnPT06MTc4YWFlYjk=
    
    print(f"结果: {result}")
    return result


async def test_batch_create_test_cases():
    """测试批量创建测试用例"""
    print("\n" + "="*60)
    print("测试 4: 批量创建测试用例")
    print("="*60)
    
    result = await batch_create_test_cases_tool(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        test_cases=[
            {
                "name": "测试用例1 - 正常登录",
                "description": "验证用户使用正确凭据登录",
                "priority": "high",
                "test_case_steps": [
                    {"step": "打开登录页面", "result": "页面正常显示"},
                    {"step": "输入正确的用户名和密码", "result": "输入成功"},
                    {"step": "点击登录按钮", "result": "成功登录"}
                ],
                "tags": ["登录", "正向测试"]
            },
            {
                "name": "测试用例2 - 错误密码",
                "description": "验证用户输入错误密码时的处理",
                "priority": "high",
                "test_case_steps": [
                    {"step": "打开登录页面", "result": "页面正常显示"},
                    {"step": "输入正确的用户名和错误的密码", "result": "输入成功"},
                    {"step": "点击登录按钮", "result": "显示错误提示"}
                ],
                "tags": ["登录", "负向测试"]
            },
            {
                "name": "测试用例3 - BDD 登录场景",
                "template": "test_case_bdd",
                "feature": "用户登录",
                "scenario": "用户使用正确凭据登录成功",
                "background": "Given 用户已注册\nAnd 用户账号状态正常",
                "tags": ["登录", "BDD"]
            }
        ]
    )
    
    print(f"结果: {result}")
    print(f"\n统计信息:")
    print(f"  总数: {result.get('data', {}).get('total', 0)}")
    print(f"  成功: {result.get('data', {}).get('succeeded', 0)}")
    print(f"  失败: {result.get('data', {}).get('failed', 0)}")
    
    return result
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U1ZKYVdnPT06MTc4YWFlYjk=


async def main():
    """运行所有测试"""
    print("\n🧪 开始测试 HTTP 工具函数...")
    print("⚠️  注意：需要确保后端服务正在运行（http://localhost:8080）")
    
    # 测试 1: 创建单个测试用例
    await test_create_test_case()
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U1ZKYVdnPT06MTc4YWFlYjk=
    
    # 测试 2: 创建 BDD 测试用例
    await test_create_bdd_test_case()
    
    # 测试 3: 更新测试用例（需要先有一个测试用例）
    # await test_update_test_case()
    
    # 测试 4: 批量创建测试用例
    await test_batch_create_test_cases()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

