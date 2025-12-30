"""
AI Agent管理器
负责与LangGraph服务交互，管理测试脚本生成和执行
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.env import LangGraphConfig, OllamaConfig
from utils.log_util import logger

try:
    from langgraph_sdk import Client
    LANGGRAPH_SDK_AVAILABLE = True
except ImportError:
    LANGGRAPH_SDK_AVAILABLE = False
    logger.warning("langgraph-sdk未安装，Agent功能将使用模拟模式")


class AgentManager:
    """AI Agent管理器"""
    
    def __init__(self, langgraph_api_url: str = None):
        """
        初始化Agent管理器
        
        Args:
            langgraph_api_url: LangGraph API服务地址
        """
        # 优先使用参数，否则使用配置中心
        self.langgraph_api_url = langgraph_api_url or LangGraphConfig.langgraph_api_url
        self.available_agents: Dict[str, Dict[str, Any]] = {}
        self.client = None
        self.mock_mode = not LANGGRAPH_SDK_AVAILABLE
        
        # 加载Agent配置
        self._load_agents_config()
        
        # 初始化LangGraph客户端
        if LANGGRAPH_SDK_AVAILABLE:
            try:
                self.client = Client(url=self.langgraph_api_url)
                logger.info(f"LangGraph客户端初始化成功: {self.langgraph_api_url}")
            except Exception as e:
                logger.warning(f"LangGraph客户端初始化失败，使用模拟模式: {e}")
                self.mock_mode = True
    
    def _load_agents_config(self):
        """加载Agent配置"""
        # 尝试从graph.json加载配置
        config_paths = [
            Path(__file__).parents[4] / "testing-agents-service" / "testing-agents-service" / "graph.json",
            Path(__file__).parents[3] / "graph.json",
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.available_agents = config.get('graphs', {})
                        logger.info(f"从{config_path}加载了{len(self.available_agents)}个Agent配置")
                        return
                except Exception as e:
                    logger.warning(f"加载Agent配置失败: {e}")
        
        # 使用默认配置
        self.available_agents = {
            'k6_agent': {
                'description': 'K6性能测试Agent，用于生成和执行K6性能测试脚本'
            },
            'ui_automation_agent': {
                'description': 'UI自动化测试Agent，使用Playwright进行Web自动化测试'
            },
            'rest_api_agent': {
                'description': 'REST API测试Agent，用于API自动化测试'
            },
            'rag_api_agent': {
                'description': 'RAG API测试Agent，集成RAG、测试生成和执行功能'
            },
            'data_agent': {
                'description': '数据Agent协调器，管理数据导入和RAG查询'
            }
        }
        logger.info("使用默认Agent配置")
    
    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """列出所有可用的Agent"""
        return [
            {
                'id': agent_id,
                'description': details.get('description', '无描述')
            }
            for agent_id, details in self.available_agents.items()
        ]
    
    async def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """获取Agent信息"""
        if agent_type in self.available_agents:
            return {
                'id': agent_type,
                **self.available_agents[agent_type]
            }
        return None
    
    async def generate_script(
        self,
        agent_type: str,
        prompt: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        使用AI Agent生成测试脚本
        
        Args:
            agent_type: Agent类型
            prompt: 生成提示词
            config: 配置参数
            
        Returns:
            生成结果
        """
        if agent_type not in self.available_agents:
            return {
                'success': False,
                'error': f'不支持的Agent类型: {agent_type}'
            }
        
        try:
            if self.mock_mode:
                # 模拟模式：生成示例脚本
                script_content = self._generate_mock_script(agent_type, prompt, config)
                return {
                    'success': True,
                    'script_content': script_content,
                    'agent_id': agent_type,
                    'thread_id': 'mock-thread-001'
                }
            
            # 调用LangGraph服务
            thread = await self.client.threads.create()
            
            # 构建消息
            messages = [{
                'role': 'user',
                'content': f"请根据以下需求生成测试脚本：\n\n{prompt}"
            }]
            
            if config:
                messages[0]['content'] += f"\n\n配置参数：{json.dumps(config, ensure_ascii=False)}"
            
            # 执行Agent
            run = await self.client.runs.create(
                thread_id=thread['thread_id'],
                assistant_id=agent_type,
                input={'messages': messages}
            )
            
            # 等待完成并获取结果
            result = await self.client.runs.join(thread['thread_id'], run['run_id'])
            
            # 解析结果
            script_content = self._extract_script_from_result(result)
            
            return {
                'success': True,
                'script_content': script_content,
                'agent_id': agent_type,
                'thread_id': thread['thread_id'],
                'run_id': run['run_id']
            }
            
        except Exception as e:
            logger.error(f"生成脚本失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_script(
        self,
        agent_type: str,
        script_content: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        使用AI Agent执行测试脚本
        
        Args:
            agent_type: Agent类型
            script_content: 脚本内容
            config: 执行配置
            
        Returns:
            执行结果
        """
        if agent_type not in self.available_agents:
            return {
                'success': False,
                'error': f'不支持的Agent类型: {agent_type}'
            }
        
        try:
            if self.mock_mode:
                # 模拟模式：返回模拟执行结果
                result = self._generate_mock_execution_result(agent_type, config)
                return {
                    'success': True,
                    'result': result,
                    'agent_id': agent_type,
                    'thread_id': 'mock-thread-002'
                }
            
            # 调用LangGraph服务执行脚本
            thread = await self.client.threads.create()
            
            messages = [{
                'role': 'user',
                'content': f"请执行以下测试脚本：\n\n```\n{script_content}\n```"
            }]
            
            if config:
                messages[0]['content'] += f"\n\n执行配置：{json.dumps(config, ensure_ascii=False)}"
            
            run = await self.client.runs.create(
                thread_id=thread['thread_id'],
                assistant_id=agent_type,
                input={'messages': messages, 'script': script_content}
            )
            
            result = await self.client.runs.join(thread['thread_id'], run['run_id'])
            
            return {
                'success': True,
                'result': self._extract_result_from_execution(result),
                'agent_id': agent_type,
                'thread_id': thread['thread_id'],
                'run_id': run['run_id']
            }
            
        except Exception as e:
            logger.error(f"执行脚本失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_mock_script(
        self,
        agent_type: str,
        prompt: str,
        config: Dict[str, Any] = None
    ) -> str:
        """生成模拟脚本"""
        if agent_type == 'k6_agent':
            return f'''import http from 'k6/http';
import {{ check, sleep }} from 'k6';

// 生成自: {prompt[:50]}...
// AI模型: {OllamaConfig.ollama_model}
export const options = {{
  vus: {config.get('vus', 10) if config else 10},
  duration: '{config.get('duration', '30s') if config else '30s'}',
  thresholds: {{
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.1'],
  }},
}};

export default function() {{
  const res = http.get('https://test.k6.io');
  
  check(res, {{
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  }});
  
  sleep(1);
}}
'''
        elif agent_type == 'ui_automation_agent':
            return f'''# 生成自: {prompt[:50]}...
# AI模型: {OllamaConfig.ollama_model}
from playwright.sync_api import sync_playwright

def test_example():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 打开页面
        page.goto('https://example.com')
        
        # 验证标题
        assert 'Example' in page.title()
        
        # 截图
        page.screenshot(path='screenshot.png')
        
        browser.close()

if __name__ == '__main__':
    test_example()
'''
        else:
            return f'''# API测试脚本
# 生成自: {prompt[:50]}...
# AI模型: {OllamaConfig.ollama_model}
import requests

def test_api():
    response = requests.get('https://api.example.com/test')
    assert response.status_code == 200
    print(f"Response: {{response.json()}}")

if __name__ == '__main__':
    test_api()
'''
    
    def _generate_mock_execution_result(
        self,
        agent_type: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成模拟执行结果"""
        import random
        
        if agent_type == 'k6_agent':
            return {
                'metrics': {
                    'http_reqs': random.randint(100, 1000),
                    'http_req_duration_avg': round(random.uniform(50, 200), 2),
                    'http_req_duration_p95': round(random.uniform(100, 400), 2),
                    'http_req_failed': round(random.uniform(0, 0.05), 4),
                    'vus': config.get('vus', 10) if config else 10,
                },
                'checks': {
                    'passed': random.randint(90, 100),
                    'failed': random.randint(0, 10)
                }
            }
        elif agent_type == 'ui_automation_agent':
            return {
                'tests_passed': random.randint(8, 10),
                'tests_failed': random.randint(0, 2),
                'screenshots': ['screenshot_1.png', 'screenshot_2.png']
            }
        else:
            return {
                'requests_made': random.randint(10, 50),
                'assertions_passed': random.randint(45, 50),
                'assertions_failed': random.randint(0, 5)
            }
    
    def _extract_script_from_result(self, result: Any) -> str:
        """从执行结果中提取脚本内容"""
        try:
            if isinstance(result, dict):
                messages = result.get('messages', [])
                for msg in reversed(messages):
                    content = msg.get('content', '')
                    if '```' in content:
                        # 提取代码块
                        import re
                        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
                        if code_blocks:
                            return code_blocks[-1].strip()
                    return content
            return str(result)
        except Exception as e:
            logger.error(f"提取脚本内容失败: {e}")
            return str(result)
    
    def _extract_result_from_execution(self, result: Any) -> Dict[str, Any]:
        """从执行结果中提取执行数据"""
        try:
            if isinstance(result, dict):
                return result.get('output', result)
            return {'raw_result': str(result)}
        except Exception as e:
            logger.error(f"提取执行结果失败: {e}")
            return {'error': str(e)}


# 全局单例
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """获取Agent管理器单例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager
