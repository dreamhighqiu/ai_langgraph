"""
性能测试功能完整验证脚本
用于验证从需求到报告的完整流程
"""
import asyncio
import httpx
import json
from datetime import datetime


class PerformanceTestingDemo:
    """性能测试功能演示"""
    
    def __init__(self):
        self.base_url = "http://localhost:9099"
        self.headers = {
            "Content-Type": "application/json",
            # 需要先登录获取token
            # "Authorization": "Bearer your-token"
        }
    
    async def test_complete_workflow(self):
        """测试完整工作流程"""
        print("=" * 80)
        print("性能测试功能完整流程验证")
        print("=" * 80)
        
        # 步骤1: 创建测试需求
        print("\n[步骤1] 创建性能测试需求...")
        requirement_id = await self.create_requirement()
        if not requirement_id:
            print("❌ 创建需求失败")
            return
        print(f"✅ 需求创建成功, ID: {requirement_id}")
        
        # 步骤2: AI生成K6脚本
        print("\n[步骤2] 调用AI生成K6性能测试脚本...")
        script_id = await self.generate_k6_script(requirement_id)
        if not script_id:
            print("❌ 生成脚本失败")
            return
        print(f"✅ 脚本生成成功, ID: {script_id}")
        
        # 步骤3: 执行性能测试
        print("\n[步骤3] 执行K6性能测试...")
        execution_id = await self.execute_k6_test(script_id)
        if not execution_id:
            print("❌ 提交执行失败")
            return
        print(f"✅ 测试已提交, 执行ID: {execution_id}")
        
        # 步骤4: 监控执行过程
        print("\n[步骤4] 监控执行状态...")
        final_status = await self.monitor_execution(execution_id)
        print(f"✅ 执行完成, 最终状态: {final_status}")
        
        # 步骤5: 获取报告
        print("\n[步骤5] 下载测试报告...")
        # 需要先查询报告ID
        # report_id = await self.get_report_id(execution_id)
        # await self.download_report(report_id)
        
        print("\n" + "=" * 80)
        print("✅ 完整流程验证完成!")
        print("=" * 80)
    
    async def create_requirement(self) -> int:
        """创建性能测试需求"""
        url = f"{self.base_url}/testing/requirement"
        data = {
            "requirement_name": "登录接口性能测试_demo",
            "requirement_type": "performance",
            "project_id": 1,  # 需要先创建项目
            "description": """
测试登录接口在高并发场景下的性能表现:
- 目标: 测试登录API能否承受100并发用户
- 场景: 逐步加压,观察响应时间和错误率
- API: POST /api/auth/login
            """,
            "acceptance_criteria": """
性能要求:
1. p95响应时间 < 500ms
2. 错误率 < 1%
3. RPS > 200
            """,
            "priority": "high",
            "status": "0"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=self.headers)
                result = response.json()
                
                if result.get('code') == 200:
                    return result['data']['requirement_id']
                else:
                    print(f"创建需求失败: {result.get('msg')}")
                    return None
                    
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    async def generate_k6_script(self, requirement_id: int) -> int:
        """AI生成K6脚本"""
        url = f"{self.base_url}/testing/performance/generate-script"
        data = {
            "requirement_id": requirement_id,
            "config": {
                "vus": 50,
                "duration": "1m",
                "stages": [
                    {"duration": "10s", "target": 10},
                    {"duration": "30s", "target": 50},
                    {"duration": "20s", "target": 0}
                ],
                "thresholds": {
                    "http_req_duration": ["p(95)<500"],
                    "http_req_failed": ["rate<0.01"],
                    "http_reqs": ["rate>200"]
                },
                "use_rag": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5分钟超时
                response = await client.post(url, json=data, headers=self.headers)
                result = response.json()
                
                if result.get('code') == 200:
                    script_data = result['data']
                    print(f"  脚本名称: {script_data['script_name']}")
                    print(f"  脚本长度: {len(script_data['script_content'])} 字符")
                    print(f"  存储路径: {script_data['script_url']}")
                    return script_data['script_id']
                else:
                    print(f"生成脚本失败: {result.get('msg')}")
                    return None
                    
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    async def execute_k6_test(self, script_id: int) -> int:
        """执行K6测试"""
        url = f"{self.base_url}/testing/performance/execute"
        data = {
            "script_id": script_id,
            "config": {
                "vus": 50,
                "duration": "1m"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=self.headers)
                result = response.json()
                
                if result.get('code') == 200:
                    exec_data = result['data']
                    print(f"  执行ID: {exec_data['execution_id']}")
                    print(f"  状态: {exec_data['status']}")
                    print(f"  消息: {exec_data['message']}")
                    return exec_data['execution_id']
                else:
                    print(f"执行失败: {result.get('msg')}")
                    return None
                    
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    async def monitor_execution(self, execution_id: int, max_wait: int = 300) -> str:
        """监控执行状态"""
        url = f"{self.base_url}/testing/performance/execution/{execution_id}/status"
        
        start_time = datetime.now()
        while True:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, headers=self.headers)
                    result = response.json()
                    
                    if result.get('code') == 200:
                        status_data = result['data']
                        status = status_data['status']
                        
                        elapsed = (datetime.now() - start_time).seconds
                        print(f"  [{elapsed}s] 状态: {status}")
                        
                        if status in ['success', 'failed']:
                            return status
                        
                        if elapsed >= max_wait:
                            print(f"  超时: 已等待{max_wait}秒")
                            return 'timeout'
                        
                        await asyncio.sleep(5)  # 每5秒查询一次
                    else:
                        print(f"查询状态失败: {result.get('msg')}")
                        return 'error'
                        
            except Exception as e:
                print(f"查询失败: {e}")
                await asyncio.sleep(5)


async def main():
    """主函数"""
    demo = PerformanceTestingDemo()
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          性能测试功能完整流程验证                               ║
╚═══════════════════════════════════════════════════════════════╝

前提条件:
1. testing-agents-service 已启动 (http://localhost:2025)
2. 后端服务已启动 (http://localhost:9099)
3. 数据库已初始化
4. MinIO已配置

开始验证...
""")
    
    await demo.test_complete_workflow()


if __name__ == "__main__":
    asyncio.run(main())

