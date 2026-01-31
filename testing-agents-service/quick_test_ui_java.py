"""
UI Java Agent 快速测试脚本

使用方式:
    cd testing-agents-service
    python quick_test_ui_java.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_ui_java_agent():
    """快速测试 UI Java Agent"""
    
    print("\n" + "=" * 70)
    print("🚀 UI Java Agent 快速测试")
    print("=" * 70)
    
    try:
        # 1. 检查配置
        print("\n📋 步骤 1: 检查配置...")
        from config.settings import settings
        from config.llm_config import get_llm_info
        
        print(f"  ✅ 工作目录: {settings.ui_java_workspace_root}")
        print(f"  ✅ Skills 目录: {settings.ui_java_skills_root}")
        
        llm_info = get_llm_info()
        print(f"  ✅ LLM Provider: {llm_info['provider']}")
        print(f"  ✅ LLM Model: {llm_info['model']}")
        print(f"  ✅ API Key: {'已配置' if llm_info['api_key_configured'] else '❌ 未配置'}")
        
        if not llm_info['api_key_configured']:
            print("\n❌ 错误: API Key 未配置")
            print("请在 .env 文件中配置 OPENAI_API_KEY")
            return
        
        # 2. 导入 Agent
        print("\n📦 步骤 2: 导入 Agent...")
        from agents.ui_java.agent import make_agent
        print("  ✅ Agent 模块导入成功")
        
        # 3. 创建 Agent 实例
        print("\n🔧 步骤 3: 创建 Agent 实例...")
        async with make_agent() as agent:
            print("  ✅ Agent 实例创建成功")
            
            # 4. 准备测试用例
            test_cases = [
                {
                    "name": "测试 1: 创建测试计划",
                    "input": "为 Google 搜索页面创建一个简单的测试计划，包括：1. 打开页面 2. 输入搜索关键词 3. 验证搜索结果"
                },
                # 可以添加更多测试用例
                # {
                #     "name": "测试 2: 生成测试代码",
                #     "input": "根据上面的测试计划，生成 Java + Playwright 测试代码"
                # },
            ]
            
            # 5. 运行测试
            for idx, test_case in enumerate(test_cases, 1):
                print(f"\n{'=' * 70}")
                print(f"🧪 {test_case['name']}")
                print(f"{'=' * 70}")
                print(f"\n💬 用户输入:\n{test_case['input']}")
                print(f"\n⏳ 正在处理...")
                
                try:
                    # 调用 Agent
                    result = await agent.ainvoke({
                        "messages": [
                            {
                                "role": "user",
                                "content": test_case['input']
                            }
                        ]
                    })
                    
                    # 提取响应
                    if "messages" in result and len(result["messages"]) > 0:
                        last_message = result["messages"][-1]
                        if hasattr(last_message, "content"):
                            response = last_message.content
                        else:
                            response = str(last_message)
                        
                        print(f"\n🤖 Agent 响应:")
                        print("-" * 70)
                        print(response[:1000])  # 只显示前 1000 字符
                        if len(response) > 1000:
                            print(f"\n... (还有 {len(response) - 1000} 个字符)")
                        print("-" * 70)
                        print(f"\n✅ 测试 {idx} 完成")
                    else:
                        print(f"\n⚠️  没有收到响应")
                
                except Exception as e:
                    print(f"\n❌ 测试 {idx} 失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n{'=' * 70}")
            print("✅ 所有测试完成")
            print(f"{'=' * 70}")
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("\n🎯 开始测试 UI Java Agent...")
    asyncio.run(test_ui_java_agent())
    print("\n✨ 测试完成！\n")

