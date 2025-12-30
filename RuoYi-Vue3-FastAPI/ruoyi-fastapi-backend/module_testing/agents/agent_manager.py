"""
AI Agent管理器
负责与LangGraph服务交互，管理测试脚本生成和执行

支持两种模式：
1. 远程模式：通过 LangGraph SDK 调用 LangGraph API 服务
2. 本地模式：直接导入并调用本地 Agent 模块
"""
import asyncio
import json
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from config.env import LangGraphConfig, OllamaConfig, OpenAIConfig
from utils.log_util import logger

# LangGraph SDK 可用性检测
LANGGRAPH_SDK_AVAILABLE = False
try:
    from langgraph_sdk import get_client
    LANGGRAPH_SDK_AVAILABLE = True
except ImportError:
    logger.warning("langgraph-sdk未安装，将尝试本地Agent模式")

# 添加 testing-agents-service 到 Python 路径
AGENTS_SERVICE_PATH = Path(__file__).parents[4] / "testing-agents-service" / "testing-agents-service"
AGENTS_SRC_PATH = AGENTS_SERVICE_PATH / "src"
if AGENTS_SRC_PATH.exists() and str(AGENTS_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(AGENTS_SRC_PATH))
    sys.path.insert(0, str(AGENTS_SERVICE_PATH))


class AgentManager:
    """AI Agent管理器 - 真实调用 LangGraph 服务"""
    
    # Agent 类型映射
    AGENT_TYPES = {
        'k6_agent': {
            'description': 'K6性能测试Agent，用于生成和执行K6性能测试脚本',
            'module': 'k6_agent.main',
            'attr': 'agent'
        },
        'rest_api_agent': {
            'description': 'REST API测试Agent，使用automation-quality-mcp进行API自动化测试',
            'module': 'api_agent.rest_api_agent',
            'attr': 'agent'
        },
        'rag_api_agent': {
            'description': 'RAG API测试Agent，集成RAG、测试生成和执行功能',
            'module': 'api_agent.rag_api_agent',
            'attr': 'agent'
        },
        'data_agent': {
            'description': '数据Agent协调器，管理数据导入和RAG查询子Agent',
            'module': 'data_agent.main_agent',
            'attr': 'agent'
        },
        'ui_automation_agent': {
            'description': 'UI自动化测试Agent，使用Playwright进行Web自动化测试',
            'module': 'ui_automation.web_automation_agent',
            'attr': 'agent'
        },
        'chat_rag_agent': {
            'description': '聊天RAG Agent，基于RAG知识库回答问题',
            'module': 'data_agent.chat_rag_agent',
            'attr': 'agent'
        },
        'data_import_agent': {
            'description': '数据导入Agent，用于爬取和导入API文档到RAG知识库',
            'module': 'data_agent.data_import_agent',
            'attr': 'agent'
        }
    }
    
    def __init__(self, langgraph_api_url: str = None):
        """
        初始化Agent管理器
        
        Args:
            langgraph_api_url: LangGraph API服务地址，默认使用配置中心
        """
        self.langgraph_api_url = langgraph_api_url or LangGraphConfig.langgraph_api_url
        self.available_agents: Dict[str, Dict[str, Any]] = {}
        self.client = None
        self.local_agents: Dict[str, Any] = {}
        self.mode = "unknown"  # remote / local / unavailable
        
        # 加载Agent配置
        self._load_agents_config()
        
        # 初始化连接
        asyncio.create_task(self._initialize_connection())
    
    def _load_agents_config(self):
        """加载Agent配置"""
        # 尝试从graph.json加载配置
        config_path = AGENTS_SERVICE_PATH / "graph.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    graphs = config.get('graphs', {})
                    for agent_id, details in graphs.items():
                        self.available_agents[agent_id] = {
                            'description': details.get('description', ''),
                            'path': details.get('path', ''),
                        }
                    logger.info(f"从{config_path}加载了{len(self.available_agents)}个Agent配置")
                    return
            except Exception as e:
                logger.warning(f"加载Agent配置失败: {e}")
        
        # 使用默认配置
        for agent_id, details in self.AGENT_TYPES.items():
            self.available_agents[agent_id] = {
                'description': details['description']
            }
        logger.info("使用默认Agent配置")
    
    async def _initialize_connection(self):
        """初始化与LangGraph服务的连接"""
        # 1. 尝试远程 LangGraph API
        if LANGGRAPH_SDK_AVAILABLE:
            try:
                self.client = get_client(url=self.langgraph_api_url)
                # 测试连接
                assistants = await self.client.assistants.search()
                self.mode = "remote"
                logger.info(f"LangGraph远程服务连接成功: {self.langgraph_api_url}, 可用Agent: {len(assistants)}")
                return
            except Exception as e:
                logger.warning(f"LangGraph远程服务连接失败: {e}")
        
        # 2. 尝试本地Agent模式
        try:
            await self._load_local_agents()
            if self.local_agents:
                self.mode = "local"
                logger.info(f"切换到本地Agent模式，已加载: {list(self.local_agents.keys())}")
                return
        except Exception as e:
            logger.warning(f"本地Agent加载失败: {e}")
        
        # 3. 都失败了
        self.mode = "unavailable"
        logger.error("Agent服务不可用：远程服务和本地Agent均无法使用")
    
    async def _load_local_agents(self):
        """加载本地Agent模块"""
        for agent_id, details in self.AGENT_TYPES.items():
            try:
                module_name = details['module']
                attr_name = details['attr']
                
                # 动态导入模块
                module = __import__(module_name, fromlist=[attr_name])
                agent = getattr(module, attr_name)
                self.local_agents[agent_id] = agent
                logger.info(f"成功加载本地Agent: {agent_id}")
            except Exception as e:
                logger.debug(f"加载本地Agent {agent_id} 失败: {e}")
    
    async def ensure_connected(self):
        """确保已连接到服务"""
        if self.mode == "unknown":
            await self._initialize_connection()
    
    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """列出所有可用的Agent"""
        await self.ensure_connected()
        
        agents = []
        for agent_id, details in self.available_agents.items():
            # 检查该Agent是否真正可用
            is_available = False
            if self.mode == "remote":
                is_available = True  # 远程模式下所有配置的Agent都可用
            elif self.mode == "local":
                is_available = agent_id in self.local_agents
            
            agents.append({
                'id': agent_id,
                'description': details.get('description', '无描述'),
                'available': is_available,
                'mode': self.mode
            })
        
        return agents
    
    async def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """获取Agent信息"""
        await self.ensure_connected()
        
        if agent_type in self.available_agents:
            is_available = False
            if self.mode == "remote":
                is_available = True
            elif self.mode == "local":
                is_available = agent_type in self.local_agents
            
            return {
                'id': agent_type,
                'available': is_available,
                'mode': self.mode,
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
        await self.ensure_connected()
        
        if agent_type not in self.available_agents:
            return {
                'success': False,
                'error': f'不支持的Agent类型: {agent_type}'
            }
        
        if self.mode == "unavailable":
            return {
                'success': False,
                'error': 'Agent服务不可用，请检查LangGraph服务是否启动'
            }
        
        try:
            # 构建消息
            message_content = f"请根据以下需求生成测试脚本：\n\n{prompt}"
            if config:
                message_content += f"\n\n配置参数：{json.dumps(config, ensure_ascii=False, indent=2)}"
            
            messages = [{'role': 'user', 'content': message_content}]
            
            if self.mode == "remote":
                # 远程调用 LangGraph API
                result = await self._call_remote_agent(agent_type, messages)
            else:
                # 本地调用 Agent
                result = await self._call_local_agent(agent_type, messages)
            
            # 提取脚本内容
            script_content = self._extract_script_from_result(result)
            
            return {
                'success': True,
                'script_content': script_content,
                'agent_id': agent_type,
                'mode': self.mode,
                'raw_result': result
            }
            
        except Exception as e:
            logger.error(f"生成脚本失败: {e}", exc_info=True)
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
        await self.ensure_connected()
        
        if agent_type not in self.available_agents:
            return {
                'success': False,
                'error': f'不支持的Agent类型: {agent_type}'
            }
        
        if self.mode == "unavailable":
            return {
                'success': False,
                'error': 'Agent服务不可用，请检查LangGraph服务是否启动'
            }
        
        try:
            # 构建执行消息
            message_content = f"请执行以下测试脚本并返回执行结果：\n\n```\n{script_content}\n```"
            if config:
                message_content += f"\n\n执行配置：{json.dumps(config, ensure_ascii=False, indent=2)}"
            
            messages = [{'role': 'user', 'content': message_content}]
            
            if self.mode == "remote":
                result = await self._call_remote_agent(agent_type, messages)
            else:
                result = await self._call_local_agent(agent_type, messages)
            
            # 解析执行结果
            execution_result = self._extract_execution_result(result)
            
            return {
                'success': True,
                'result': execution_result,
                'agent_id': agent_type,
                'mode': self.mode,
                'raw_result': result
            }
            
        except Exception as e:
            logger.error(f"执行脚本失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def chat(
        self,
        agent_type: str,
        message: str,
        thread_id: str = None
    ) -> Dict[str, Any]:
        """
        与Agent进行对话（支持多轮会话）
        
        Args:
            agent_type: Agent类型
            message: 用户消息
            thread_id: 会话ID（用于多轮对话）
            
        Returns:
            对话结果
        """
        await self.ensure_connected()
        
        if agent_type not in self.available_agents:
            return {
                'success': False,
                'error': f'不支持的Agent类型: {agent_type}'
            }
        
        if self.mode == "unavailable":
            return {
                'success': False,
                'error': 'Agent服务不可用'
            }
        
        try:
            messages = [{'role': 'user', 'content': message}]
            
            if self.mode == "remote":
                result = await self._call_remote_agent(agent_type, messages, thread_id)
            else:
                result = await self._call_local_agent(agent_type, messages)
            
            # 提取回复内容
            reply = self._extract_reply_from_result(result)
            
            return {
                'success': True,
                'reply': reply,
                'agent_id': agent_type,
                'thread_id': result.get('thread_id'),
                'mode': self.mode
            }
            
        except Exception as e:
            logger.error(f"对话失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _call_remote_agent(
        self,
        agent_type: str,
        messages: List[Dict],
        thread_id: str = None
    ) -> Dict[str, Any]:
        """调用远程LangGraph API"""
        if not self.client:
            raise RuntimeError("LangGraph客户端未初始化")
        
        # 创建或使用现有线程
        if thread_id:
            thread = {'thread_id': thread_id}
        else:
            thread = await self.client.threads.create()
        
        # 创建运行
        run = await self.client.runs.create(
            thread_id=thread['thread_id'],
            assistant_id=agent_type,
            input={'messages': messages}
        )
        
        # 等待完成
        result = await self.client.runs.join(thread['thread_id'], run['run_id'])
        
        return {
            'messages': result.get('messages', []),
            'thread_id': thread['thread_id'],
            'run_id': run['run_id'],
            'output': result
        }
    
    async def _call_local_agent(
        self,
        agent_type: str,
        messages: List[Dict]
    ) -> Dict[str, Any]:
        """调用本地Agent"""
        if agent_type not in self.local_agents:
            raise RuntimeError(f"本地Agent {agent_type} 未加载")
        
        agent = self.local_agents[agent_type]
        
        # 调用Agent
        result = await agent.ainvoke({
            'messages': messages
        })
        
        return {
            'messages': result.get('messages', []),
            'output': result
        }
    
    def _extract_script_from_result(self, result: Dict[str, Any]) -> str:
        """从执行结果中提取脚本内容"""
        try:
            messages = result.get('messages', [])
            for msg in reversed(messages):
                content = msg.get('content', '') if isinstance(msg, dict) else getattr(msg, 'content', '')
                if content and '```' in str(content):
                    # 提取代码块
                    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', str(content), re.DOTALL)
                    if code_blocks:
                        return code_blocks[-1].strip()
                if content:
                    return str(content)
            
            # 如果没有找到消息，返回原始输出
            output = result.get('output', {})
            if isinstance(output, dict):
                return json.dumps(output, ensure_ascii=False, indent=2)
            return str(output)
        except Exception as e:
            logger.error(f"提取脚本内容失败: {e}")
            return str(result)
    
    def _extract_execution_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """从执行结果中提取执行数据"""
        try:
            messages = result.get('messages', [])
            for msg in reversed(messages):
                content = msg.get('content', '') if isinstance(msg, dict) else getattr(msg, 'content', '')
                if content:
                    # 尝试解析JSON结果
                    try:
                        # 查找JSON块
                        json_match = re.search(r'```json\n(.*?)```', str(content), re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group(1))
                    except:
                        pass
                    
                    return {'message': str(content)}
            
            return result.get('output', {'raw': str(result)})
        except Exception as e:
            logger.error(f"提取执行结果失败: {e}")
            return {'error': str(e)}
    
    def _extract_reply_from_result(self, result: Dict[str, Any]) -> str:
        """从结果中提取回复内容"""
        try:
            messages = result.get('messages', [])
            for msg in reversed(messages):
                content = msg.get('content', '') if isinstance(msg, dict) else getattr(msg, 'content', '')
                if content:
                    return str(content)
            return "无回复内容"
        except Exception as e:
            logger.error(f"提取回复内容失败: {e}")
            return str(result)
    
    async def import_data(
        self,
        url: str,
        data_type: str = "api_doc"
    ) -> Dict[str, Any]:
        """
        导入数据到RAG知识库
        
        Args:
            url: 数据源URL
            data_type: 数据类型 (api_doc, web_page, etc.)
            
        Returns:
            导入结果
        """
        message = f"请导入以下URL的{data_type}到RAG知识库：{url}"
        return await self.chat('data_import_agent', message)
    
    async def query_knowledge(self, question: str) -> Dict[str, Any]:
        """
        查询RAG知识库
        
        Args:
            question: 查询问题
            
        Returns:
            查询结果
        """
        return await self.chat('chat_rag_agent', question)
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        await self.ensure_connected()
        
        return {
            'mode': self.mode,
            'langgraph_api_url': self.langgraph_api_url,
            'sdk_available': LANGGRAPH_SDK_AVAILABLE,
            'remote_connected': self.mode == 'remote',
            'local_agents_loaded': list(self.local_agents.keys()),
            'available_agents': list(self.available_agents.keys())
        }


# 全局单例
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """获取Agent管理器单例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


async def reset_agent_manager():
    """重置Agent管理器（用于重新初始化连接）"""
    global _agent_manager
    _agent_manager = None
    return get_agent_manager()
