"""
LangGraph API Client - 用于调用 testing-agents-service
"""
import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime
import httpx
from utils.log_util import logger


class LangGraphClient:
    """LangGraph API 客户端，用于调用 testing-agents-service 的 Agents"""
    
    def __init__(self, base_url: str = "http://localhost:2025"):
        """
        初始化客户端
        
        Args:
            base_url: LangGraph API 服务地址，默认 http://localhost:2025
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = httpx.Timeout(300.0, connect=10.0)  # 5分钟超时，连接10秒
        
    async def check_health(self) -> bool:
        """检查 LangGraph API 服务健康状态"""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(f"{self.base_url}/ok")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"LangGraph服务健康检查失败: {e}")
            return False
    
    async def list_assistants(self) -> List[Dict[str, Any]]:
        """获取所有可用的 Assistant (Agent) 列表"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/assistants")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取Assistant列表失败: {e}")
            return []
    
    async def get_assistant(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """获取指定 Assistant 的详细信息"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/assistants/{assistant_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取Assistant详情失败 [{assistant_id}]: {e}")
            return None
    
    async def create_thread(self) -> Optional[str]:
        """创建一个新的对话线程"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/threads",
                    json={}
                )
                response.raise_for_status()
                result = response.json()
                return result.get('thread_id')
        except Exception as e:
            logger.error(f"创建Thread失败: {e}")
            return None
    
    async def invoke_agent(
        self,
        assistant_id: str,
        message: str,
        thread_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        同步调用 Agent 并等待结果
        
        Args:
            assistant_id: Agent ID (如 k6_agent, ui_automation_agent, rest_api_agent)
            message: 用户消息/需求描述
            thread_id: 可选的线程ID，用于维持对话上下文
            config: 可选的配置参数
            
        Returns:
            包含 Agent 响应的字典
        """
        try:
            # 如果没有提供 thread_id，创建一个新的
            if not thread_id:
                thread_id = await self.create_thread()
                if not thread_id:
                    raise Exception("无法创建对话线程")
            
            # 构建请求体
            payload = {
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": message
                        }
                    ]
                },
                "config": config or {},
                "stream_mode": "values"
            }
            
            logger.info(f"调用Agent [{assistant_id}] - Thread [{thread_id}]")
            logger.debug(f"请求消息: {message[:200]}...")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/threads/{thread_id}/runs",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                # 解析响应
                result = response.json()
                
                # 提取最后一条消息
                messages = result.get('messages', [])
                if messages:
                    last_message = messages[-1]
                    content = last_message.get('content', '')
                    
                    return {
                        'success': True,
                        'content': content,
                        'thread_id': thread_id,
                        'assistant_id': assistant_id,
                        'messages': messages,
                        'metadata': result.get('metadata', {})
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Agent未返回任何消息',
                        'thread_id': thread_id
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"Agent调用超时 [{assistant_id}]")
            return {
                'success': False,
                'error': 'Agent调用超时（5分钟），请检查测试复杂度或增加超时时间',
                'thread_id': thread_id
            }
        except Exception as e:
            logger.error(f"Agent调用失败 [{assistant_id}]: {e}")
            return {
                'success': False,
                'error': str(e),
                'thread_id': thread_id
            }
    
    async def stream_agent(
        self,
        assistant_id: str,
        message: str,
        thread_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用 Agent，实时返回结果
        
        Args:
            assistant_id: Agent ID
            message: 用户消息
            thread_id: 可选的线程ID
            config: 可选的配置参数
            
        Yields:
            Agent 的流式响应
        """
        try:
            if not thread_id:
                thread_id = await self.create_thread()
                if not thread_id:
                    raise Exception("无法创建对话线程")
            
            payload = {
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": message
                        }
                    ]
                },
                "config": config or {},
                "stream_mode": "messages"
            }
            
            logger.info(f"流式调用Agent [{assistant_id}] - Thread [{thread_id}]")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/threads/{thread_id}/runs/stream",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # 移除 "data: " 前缀
                            if data and data != "[DONE]":
                                try:
                                    chunk = json.loads(data)
                                    yield chunk
                                except json.JSONDecodeError:
                                    continue
                                    
        except Exception as e:
            logger.error(f"Agent流式调用失败 [{assistant_id}]: {e}")
            yield {
                'error': str(e),
                'thread_id': thread_id
            }
    
    async def get_thread_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取线程状态"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/threads/{thread_id}/state")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取Thread状态失败 [{thread_id}]: {e}")
            return None
    
    async def get_thread_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """获取线程的对话历史"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/threads/{thread_id}/history")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取Thread历史失败 [{thread_id}]: {e}")
            return []


# 全局客户端实例
_langgraph_client: Optional[LangGraphClient] = None


def get_langgraph_client() -> LangGraphClient:
    """获取全局 LangGraph 客户端实例（单例模式）"""
    global _langgraph_client
    if _langgraph_client is None:
        _langgraph_client = LangGraphClient()
    return _langgraph_client


def reset_langgraph_client():
    """重置全局客户端实例（用于测试或重新配置）"""
    global _langgraph_client
    _langgraph_client = None

