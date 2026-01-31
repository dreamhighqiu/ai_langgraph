"""
UI Java Agent HTTP API 测试脚本

前提: 需要先启动 LangGraph 服务
    langgraph dev

使用方式:
    python test_ui_java_http.py
"""

import requests
import json
import time

# Agent 端点
AGENT_URL = "http://localhost:2025/ui_java_agent/invoke"
HEALTH_URL = "http://localhost:2025/ok"

def check_service():
    """检查服务是否运行"""
    print("🔍 检查服务状态...")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ LangGraph 服务正常运行")
            return True
        else:
            print(f"⚠️  服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务: {e}")
        print("\n请先启动 LangGraph 服务:")
        print("  cd testing-agents-service")
        print("  langgraph dev")
        return False

def test_agent(user_message: str, test_name: str = "测试"):
    """测试 Agent"""
    print(f"\n{'=' * 70}")
    print(f"🧪 {test_name}")
    print(f"{'=' * 70}")
    
    payload = {
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
    }
    
    print(f"\n💬 用户输入:\n{user_message}")
    print(f"\n⏳ 正在发送请求...")
    
    try:
        start_time = time.time()
        response = requests.post(AGENT_URL, json=payload, timeout=120)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 响应成功 (耗时: {elapsed_time:.2f}秒)")
            
            # 提取 Agent 响应
            if "output" in result and "messages" in result["output"]:
                messages = result["output"]["messages"]
                if messages:
                    last_msg = messages[-1]
                    if "content" in last_msg:
                        content = last_msg["content"]
                        print(f"\n🤖 Agent 响应:")
                        print("-" * 70)
                        print(content[:1000])  # 只显示前 1000 字符
                        if len(content) > 1000:
                            print(f"\n... (还有 {len(content) - 1000} 个字符)")
                        print("-" * 70)
            
            # 保存完整响应到文件
            output_file = f"response_{int(time.time())}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n📄 完整响应已保存到: {output_file}")
            
            return result
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    
    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时（超过 120 秒）")
        return None
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 UI Java Agent HTTP API 测试")
    print("=" * 70)
    
    # 1. 检查服务
    if not check_service():
        return
    
    # 2. 运行测试用例
    test_cases = [
        {
            "name": "测试 1: 创建测试计划",
            "message": """
帮我为以下网站创建一个测试计划：
- 网站: https://www.google.com
- 功能: 搜索功能
- 测试场景: 
  1. 打开首页
  2. 输入搜索关键词 "LangGraph"
  3. 点击搜索按钮
  4. 验证搜索结果页面显示
"""
        },
        # 可以添加更多测试用例
        # {
        #     "name": "测试 2: 生成测试代码",
        #     "message": "根据上面的测试计划，生成完整的 Java + Playwright 测试代码"
        # },
    ]
    
    for test_case in test_cases:
        result = test_agent(
            user_message=test_case["message"],
            test_name=test_case["name"]
        )
        
        if result is None:
            print(f"\n⚠️  {test_case['name']} 失败")
            break
        
        # 等待一下再执行下一个测试
        time.sleep(2)
    
    print(f"\n{'=' * 70}")
    print("✅ 测试完成")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    main()

