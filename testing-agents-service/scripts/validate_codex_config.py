#!/usr/bin/env python3
"""验证 OpenAI Codex 配置"""

import asyncio
import httpx
from langchain_openai import ChatOpenAI

# 你提供的配置
# API_KEY = "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"
# MODEL = "gpt-5.2"
# BASE_URL = "https://us.api.openai.com/v1"


API_KEY = "sk-f868dcc5b0494e6081ff89f08584b187"
MODEL = "deepseek-chat"
BASE_URL = "https://api.deepseek.com/v1"

async def test_api_direct():
    """直接测试 API 端点"""
    print("=" * 70)
    print("步骤 1: 直接测试 API 端点")
    print("=" * 70)
    
    print(f"\n配置信息:")
    print(f"  API Key: {API_KEY[:30]}...{API_KEY[-10:]}")
    print(f"  Model: {MODEL}")
    print(f"  Base URL: {BASE_URL}")
    
    # 测试 API 端点连通性
    print(f"\n正在测试端点连通性...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 测试 models 端点
            url = f"{BASE_URL}/models"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            print(f"  请求 URL: {url}")
            response = await client.get(url, headers=headers)
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("  [OK] API 端点连通，Key 验证通过")
                data = response.json()
                print(f"  可用模型数量: {len(data.get('data', []))}")
                
                # 检查目标模型是否存在
                models = [m['id'] for m in data.get('data', [])]
                if MODEL in models:
                    print(f"  [OK] 找到模型: {MODEL}")
                else:
                    print(f"  [WARN] 未找到模型 {MODEL}")
                    print(f"  可用的类似模型:")
                    for m in models:
                        if 'gpt' in m.lower():
                            print(f"    - {m}")
                
                return True
            elif response.status_code == 401:
                print(f"  [FAIL] 认证失败 (401)")
                print(f"  响应: {response.text}")
                return False
            elif response.status_code == 404:
                print(f"  [FAIL] 端点不存在 (404)")
                print(f"  响应: {response.text}")
                return False
            else:
                print(f"  [FAIL] 请求失败")
                print(f"  响应: {response.text}")
                return False
                
        except httpx.ConnectError as e:
            print(f"  [FAIL] 连接失败: {e}")
            return False
        except Exception as e:
            print(f"  [FAIL] 错误: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_langchain():
    """测试 LangChain ChatOpenAI"""
    print("\n" + "=" * 70)
    print("步骤 2: 测试 LangChain ChatOpenAI")
    print("=" * 70)
    
    try:
        print(f"\n正在创建 ChatOpenAI 实例...")
        llm = ChatOpenAI(
            model=MODEL,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.0,
        )
        print("  [OK] ChatOpenAI 实例创建成功")
        
        print(f"\n正在测试 API 调用...")
        response = await llm.ainvoke("Say 'OK' if you receive this")
        print(f"  [OK] API 调用成功！")
        print(f"  响应: {response.content}")
        return True
        
    except Exception as e:
        print(f"  [FAIL] API 调用失败")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {e}")
        
        # 检查是否是认证错误
        error_str = str(e).lower()
        if '401' in error_str or 'unauthorized' in error_str:
            print(f"\n  [诊断] API Key 认证失败")
            print(f"     - 请检查 API Key 是否正确")
            print(f"     - 请检查 API Key 是否已过期")
            print(f"     - 请检查 API Key 权限")
        elif '404' in error_str:
            print(f"\n  [诊断] 模型或端点不存在")
            print(f"     - Base URL 可能不正确")
            print(f"     - 模型名称可能不正确")
        
        import traceback
        print(f"\n详细错误信息:")
        traceback.print_exc()
        return False

async def main():
    print("\nOpenAI Codex 配置验证工具")
    print("=" * 70)
    
    # 步骤 1: 测试 API 端点
    api_ok = await test_api_direct()
    
    if not api_ok:
        print("\n" + "=" * 70)
        print("[WARN] API 端点测试失败，建议:")
        print("=" * 70)
        print("1. 检查 Base URL 是否正确")
        print("2. 尝试使用标准端点: https://api.openai.com/v1")
        print("3. 检查 API Key 是否有效")
        print("\n继续测试 LangChain...")
    
    # 步骤 2: 测试 LangChain
    langchain_ok = await test_langchain()
    
    # 总结
    print("\n" + "=" * 70)
    print("验证结果总结")
    print("=" * 70)
    print(f"API 端点测试: {'[OK] 通过' if api_ok else '[FAIL] 失败'}")
    print(f"LangChain 测试: {'[OK] 通过' if langchain_ok else '[FAIL] 失败'}")
    
    if api_ok and langchain_ok:
        print("\n[SUCCESS] 配置完全正确，可以使用！")
    elif langchain_ok:
        print("\n[OK] LangChain 可以正常工作")
    else:
        print("\n[FAIL] 配置存在问题，需要修正")

if __name__ == "__main__":
    asyncio.run(main())

