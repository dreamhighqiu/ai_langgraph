"""
Agent Manager V2 - 基于 LangGraph API 的真实实现
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from utils.log_util import logger
from module_testing.agents.langgraph_client import get_langgraph_client, LangGraphClient


# Agent 类型映射配置
AGENT_TYPE_MAPPING = {
    'k6_agent': {
        'id': 'k6_agent',
        'name': 'K6性能测试Agent',
        'description': 'K6 性能测试 Agent，用于生成和执行 K6 性能测试脚本',
        'test_type': 'performance',
        'script_extension': '.js',
        'capabilities': ['脚本生成', '性能测试执行', '报告生成', 'RAG知识查询']
    },
    'ui_automation_agent': {
        'id': 'ui_automation_agent',
        'name': 'UI自动化测试Agent',
        'description': 'UI 自动化测试 Agent，使用 Playwright 进行 Web 自动化测试',
        'test_type': 'ui',
        'script_extension': '.spec.ts',
        'capabilities': ['脚本生成', 'Playwright测试执行', 'Allure报告', '截图录屏']
    },
    'rest_api_agent': {
        'id': 'rest_api_agent',
        'name': 'REST API测试Agent',
        'description': 'REST API 测试 Agent，使用 automation-quality-mcp 进行 API 自动化测试',
        'test_type': 'api',
        'script_extension': '.py',
        'capabilities': ['API测试生成', '自动化执行', '错误修复', '测试报告']
    },
    'rag_api_agent': {
        'id': 'rag_api_agent',
        'name': 'RAG API测试Agent',
        'description': 'RAG API 测试 Agent，集成 RAG、测试生成和执行功能',
        'test_type': 'api',
        'script_extension': '.py',
        'capabilities': ['RAG增强', 'API测试生成', '智能测试', '知识库查询']
    },
    'data_import_agent': {
        'id': 'data_import_agent',
        'name': '数据导入Agent',
        'description': '数据导入 Agent，用于爬取和导入 API 文档到 RAG 知识库',
        'test_type': 'data',
        'script_extension': '',
        'capabilities': ['网页爬取', '数据导入', 'RAG知识库管理']
    },
    'chat_rag_agent': {
        'id': 'chat_rag_agent',
        'name': 'RAG对话Agent',
        'description': '聊天 RAG Agent，基于 RAG 知识库回答问题',
        'test_type': 'chat',
        'script_extension': '',
        'capabilities': ['知识问答', 'RAG检索', '智能对话']
    },
    'data_agent': {
        'id': 'data_agent',
        'name': '数据Agent协调器',
        'description': '数据 Agent 协调器，管理数据导入和 RAG 查询子 Agent',
        'test_type': 'data',
        'script_extension': '',
        'capabilities': ['数据协调', 'Agent管理', 'RAG服务']
    }
}


class AgentManager:
    """Agent Manager V2 - 真实的 LangGraph API 集成"""
    
    def __init__(self, langgraph_url: str = "http://localhost:2025"):
        """
        初始化 Agent Manager
        
        Args:
            langgraph_url: LangGraph API 服务地址
        """
        self.langgraph_url = langgraph_url
        self.client: LangGraphClient = get_langgraph_client()
        self._service_available: Optional[bool] = None
        self._available_agents: List[str] = []
        
    async def check_service_status(self) -> Dict[str, Any]:
        """检查 LangGraph 服务状态"""
        try:
            is_healthy = await self.client.check_health()
            
            if is_healthy:
                # 获取可用的 Agents
                assistants = await self.client.list_assistants()
                available_agent_ids = [a['assistant_id'] for a in assistants] if assistants else []
                
                self._service_available = True
                self._available_agents = available_agent_ids
                
                return {
                    'status': 'online',
                    'service_url': self.langgraph_url,
                    'available_agents': available_agent_ids,
                    'total_agents': len(available_agent_ids),
                    'checked_at': datetime.now().isoformat()
                }
            else:
                self._service_available = False
                return {
                    'status': 'offline',
                    'service_url': self.langgraph_url,
                    'error': 'LangGraph服务无响应，请检查服务是否启动',
                    'checked_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self._service_available = False
            logger.error(f"检查服务状态失败: {e}")
            return {
                'status': 'error',
                'service_url': self.langgraph_url,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """
        获取所有可用的 Agents
        
        Returns:
            Agent 列表，包含详细信息
        """
        result = []
        
        try:
            # 先检查服务状态
            if self._service_available is None:
                await self.check_service_status()
            
            # 如果服务不可用，返回配置的静态列表
            if not self._service_available:
                for agent_id, config in AGENT_TYPE_MAPPING.items():
                    result.append({
                        **config,
                        'status': 'unavailable',
                        'message': 'LangGraph服务未启动'
                    })
                return result
            
            # 服务可用，获取实际的 Agents
            for agent_id, config in AGENT_TYPE_MAPPING.items():
                is_available = agent_id in self._available_agents
                
                agent_info = {
                    **config,
                    'status': 'available' if is_available else 'not_deployed',
                    'service_url': f"{self.langgraph_url}/assistants/{agent_id}"
                }
                
                result.append(agent_info)
            
            return result
            
        except Exception as e:
            logger.error(f"获取Agent列表失败: {e}")
            # 返回静态配置
            for agent_id, config in AGENT_TYPE_MAPPING.items():
                result.append({
                    **config,
                    'status': 'error',
                    'error': str(e)
                })
            return result
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定 Agent 的详细信息
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 信息字典
        """
        try:
            # 先从配置中获取基本信息
            if agent_id not in AGENT_TYPE_MAPPING:
                return None
            
            base_info = AGENT_TYPE_MAPPING[agent_id].copy()
            
            # 尝试从 LangGraph 获取实时信息
            assistant_info = await self.client.get_assistant(agent_id)
            if assistant_info:
                base_info.update({
                    'status': 'available',
                    'langgraph_info': assistant_info
                })
            else:
                base_info['status'] = 'unavailable'
            
            return base_info
            
        except Exception as e:
            logger.error(f"获取Agent信息失败 [{agent_id}]: {e}")
            return None
    
    async def generate_script(
        self,
        agent_id: str,
        requirement: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用 Agent 生成测试脚本
        
        Args:
            agent_id: Agent ID (k6_agent, ui_automation_agent, rest_api_agent)
            requirement: 需求信息
            config: 可选配置
            
        Returns:
            包含生成的脚本和元数据的字典
        """
        try:
            logger.info(f"开始生成脚本 - Agent: {agent_id}, 需求: {requirement.get('requirement_name')}")
            
            # 构建提示词
            prompt = self._build_generation_prompt(requirement, agent_id)
            
            # 调用 Agent
            result = await self.client.invoke_agent(
                assistant_id=agent_id,
                message=prompt,
                config=config
            )
            
            if result.get('success'):
                content = result.get('content', '')
                
                # 提取脚本内容（从markdown代码块中提取）
                script_content = self._extract_script_from_response(content, agent_id)
                
                return {
                    'success': True,
                    'script_content': script_content,
                    'full_response': content,
                    'thread_id': result.get('thread_id'),
                    'agent_id': agent_id,
                    'generated_at': datetime.now().isoformat(),
                    'metadata': {
                        'requirement_id': requirement.get('requirement_id'),
                        'requirement_name': requirement.get('requirement_name'),
                        'requirement_type': requirement.get('requirement_type')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Agent调用失败'),
                    'agent_id': agent_id
                }
                
        except Exception as e:
            logger.error(f"生成脚本失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id
            }
    
    async def execute_script(
        self,
        agent_id: str,
        script_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用 Agent 执行测试脚本
        
        Args:
            agent_id: Agent ID
            script_path: 脚本路径
            config: 可选配置
            
        Returns:
            执行结果
        """
        try:
            logger.info(f"开始执行脚本 - Agent: {agent_id}, 脚本: {script_path}")
            
            # 读取脚本内容
            script_content = Path(script_path).read_text(encoding='utf-8')
            
            # 构建执行提示
            prompt = f"""请执行以下脚本并返回测试结果：

脚本路径: {script_path}

脚本内容:
```
{script_content}
```

请执行测试并返回详细结果。
"""
            
            # 调用 Agent
            result = await self.client.invoke_agent(
                assistant_id=agent_id,
                message=prompt,
                config=config
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'output': result.get('content'),
                    'thread_id': result.get('thread_id'),
                    'agent_id': agent_id,
                    'executed_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error'),
                    'agent_id': agent_id
                }
                
        except Exception as e:
            logger.error(f"执行脚本失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id
            }
    
    async def analyze_requirement(
        self,
        requirement: Dict[str, Any],
        analysis_type: str = 'feasibility'
    ) -> Dict[str, Any]:
        """
        AI 分析需求
        
        Args:
            requirement: 需求信息
            analysis_type: 分析类型 (feasibility/complexity/risk)
            
        Returns:
            分析结果
        """
        try:
            # 根据需求类型选择合适的 Agent
            req_type = requirement.get('requirement_type', 'api')
            agent_id = self._get_agent_for_type(req_type)
            
            # 构建分析提示
            analysis_prompts = {
                'feasibility': f"""请分析以下测试需求的可行性：

需求名称: {requirement.get('requirement_name')}
需求类型: {requirement.get('requirement_type')}
需求描述: {requirement.get('description')}
验收标准: {requirement.get('acceptance_criteria')}

请从技术可行性、工具支持、实施难度等角度进行分析。
""",
                'complexity': f"""请评估以下测试需求的复杂度：

需求名称: {requirement.get('requirement_name')}
需求描述: {requirement.get('description')}

请评估实施复杂度、时间估算、资源需求等。
""",
                'risk': f"""请识别以下测试需求的风险点：

需求名称: {requirement.get('requirement_name')}
需求描述: {requirement.get('description')}

请识别潜在风险、技术难点和注意事项。
"""
            }
            
            prompt = analysis_prompts.get(analysis_type, analysis_prompts['feasibility'])
            
            # 调用 Agent
            result = await self.client.invoke_agent(
                assistant_id=agent_id,
                message=prompt
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'analysis': result.get('content'),
                    'analysis_type': analysis_type,
                    'agent_id': agent_id,
                    'analyzed_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error'),
                    'analysis_type': analysis_type
                }
                
        except Exception as e:
            logger.error(f"需求分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis_type': analysis_type
            }
    
    def _build_generation_prompt(self, requirement: Dict[str, Any], agent_id: str) -> str:
        """构建脚本生成提示词"""
        req_name = requirement.get('requirement_name', '未命名需求')
        req_desc = requirement.get('description', '')
        acceptance = requirement.get('acceptance_criteria', '')
        
        # 根据 Agent 类型定制提示词
        if agent_id == 'k6_agent':
            return f"""请生成K6性能测试脚本来满足以下需求：

需求名称: {req_name}
需求描述: {req_desc}
验收标准: {acceptance}

请生成完整的K6测试脚本，包括：
1. 虚拟用户配置
2. 测试场景
3. 性能阈值
4. 请求和断言

请使用最佳实践，确保脚本可直接执行。
"""
        
        elif agent_id == 'ui_automation_agent':
            return f"""请生成Playwright UI自动化测试脚本来满足以下需求：

需求名称: {req_name}
需求描述: {req_desc}
验收标准: {acceptance}

请生成完整的Playwright测试脚本，包括：
1. 浏览器配置
2. 测试步骤
3. 断言验证
4. 异常处理

请使用TypeScript，确保脚本可在Playwright中执行。
"""
        
        else:  # API agents
            return f"""请生成API自动化测试脚本来满足以下需求：

需求名称: {req_name}
需求描述: {req_desc}
验收标准: {acceptance}

请生成完整的API测试脚本，包括：
1. API请求配置
2. 测试用例
3. 数据验证
4. 错误处理

请确保脚本可直接执行测试。
"""
    
    def _extract_script_from_response(self, response: str, agent_id: str) -> str:
        """从 Agent 响应中提取脚本内容"""
        import re
        
        # 获取脚本文件扩展名
        extension = AGENT_TYPE_MAPPING.get(agent_id, {}).get('script_extension', '')
        
        # 尝试提取代码块
        # 匹配 ```javascript, ```typescript, ```python 等
        code_block_pattern = r'```[\w]*\n(.*?)```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            # 返回最长的代码块（通常是主要脚本）
            return max(matches, key=len).strip()
        
        # 如果没有代码块，返回整个响应
        return response.strip()
    
    def _get_agent_for_type(self, test_type: str) -> str:
        """根据测试类型获取对应的 Agent ID"""
        type_to_agent = {
            'performance': 'k6_agent',
            'ui': 'ui_automation_agent',
            'api': 'rest_api_agent'
        }
        return type_to_agent.get(test_type, 'rest_api_agent')


# 全局实例
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """获取全局 Agent Manager 实例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


def reset_agent_manager():
    """重置全局 Agent Manager"""
    global _agent_manager
    _agent_manager = None

