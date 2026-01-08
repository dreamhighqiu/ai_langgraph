"""
测试创建测试用例工具的 URL 构建是否正确
"""


import asyncio
from app.agents.tools import create_test_case_tool, update_test_case_tool

async def test_create_url():
    """测试创建测试用例的 URL 是否正确"""
    print("测试创建测试用例工具...")
    
    result = await create_test_case_tool(
        project_identifier="PR-1",
        folder_id="73cc8580-ef78-4608-b2b9-a83e406d4c7d",
        name="测试用例",
        description="这是一个测试用例",
        test_case_steps=[
            {"step": "步骤1", "result": "结果1"}
        ]
    )
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVVOUVN3PT06M2NjYTFhZDk=
    
    print(f"创建结果: {result}")
    
    if result.get("success"):
        print("✅ 测试用例创建成功！")
        test_case_id = result.get("data", {}).get("identifier")
        
        if test_case_id:
            print(f"\n测试更新测试用例工具...")
            update_result = await update_test_case_tool(
                project_identifier="PR-1",
                test_case_identifier=test_case_id,
                priority="high"
            )
            print(f"更新结果: {update_result}")
            
            if update_result.get("success"):
                print("✅ 测试用例更新成功！")
            else:
                print(f"❌ 测试用例更新失败: {update_result.get('error')}")
    else:
        print(f"❌ 测试用例创建失败: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_create_url())

# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVVOUVN3PT06M2NjYTFhZDk=
