"""
API测试Agent编排器

基于DeepAgents框架实现的API自动化测试编排器。
使用SubAgent模式实现灵活的任务调度。
"""


import asyncio
import os
import logging
import sys
import importlib.util
import importlib
from typing import Optional, Sequence, Any, Awaitable, Callable
from pathlib import Path

# 解决命名冲突：确保从已安装的 mcp 包导入，而不是本地的 mcp 目录
# 如果本地 mcp 模块已经在 sys.modules 中，先移除它
_local_mcp_path = str(Path(__file__).parent.parent.parent / "mcp" / "__init__.py")
if 'mcp' in sys.modules:
    existing_module = sys.modules['mcp']
    if hasattr(existing_module, '__file__') and existing_module.__file__:
        if _local_mcp_path in existing_module.__file__ or 'testing-agents-service' in existing_module.__file__:
            # 这是本地模块，需要移除并导入外部包
            del sys.modules['mcp']
            if 'mcp.types' in sys.modules:
                del sys.modules['mcp.types']

# 现在强制导入已安装的外部 mcp 包
try:
    spec = importlib.util.find_spec("mcp")
    if spec and spec.origin and 'site-packages' in spec.origin:
        # 这是已安装的包，强制导入并注册
        external_mcp = importlib.import_module("mcp")
        sys.modules['mcp'] = external_mcp
        # 导入 mcp.types
        try:
            mcp_types = importlib.import_module("mcp.types")
            sys.modules['mcp.types'] = mcp_types
        except ImportError:
            # 如果 mcp.types 不存在，尝试从 mcp 包中获取
            if hasattr(external_mcp, 'types'):
                sys.modules['mcp.types'] = external_mcp.types
except Exception:
    # 如果无法导入外部包，继续使用默认导入（可能会失败，但至少不会静默失败）
    pass

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from mcp.types import CallToolResult, TextContent
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkU1SllRPT06OWYzODVhMDU=

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.subagents import SubAgent

from api_agent.core.config import AgentConfig, get_config
from api_agent.agents.definitions import get_all_subagents
from api_agent.prompts.templates import ORCHESTRATOR_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class ContentNormalizerInterceptor:
    """
    MCP工具调用拦截器，用于规范化工具返回的内容格式。

    某些LLM API（如DeepSeek）不支持内容块列表格式，只接受纯字符串。
    此拦截器会将多个TextContent块合并为单个字符串。
    """

    async def __call__(
        self,
        request: Any,
        handler: Callable[[Any], Awaitable[Any]],
    ) -> Any:
        """
        拦截MCP工具调用，规范化返回结果的内容格式。

        Args:
            request: MCP工具调用请求
            handler: 下一个处理器

        Returns:
            规范化后的工具调用结果
        """
        # 调用原始处理器
        result = await handler(request)

        # 如果是 CallToolResult，将内容块列表转换为单个 TextContent
        if isinstance(result, CallToolResult) and result.content:
            # 提取所有文本内容并合并
            text_parts = []
            for content in result.content:
                if isinstance(content, TextContent):
                    text_parts.append(content.text)
                elif hasattr(content, 'text'):
                    text_parts.append(str(content.text))
                else:
                    # 对于非文本内容，转换为字符串表示
                    text_parts.append(str(content))

            # 合并为单个文本内容
            merged_text = "\n".join(text_parts)

            # 创建新的 CallToolResult，只包含一个 TextContent
            return CallToolResult(
                content=[TextContent(type="text", text=merged_text)],
                isError=result.isError,
            )

        return result

#
# def create_mcp_tools(config: AgentConfig) -> Sequence[BaseTool]:
#     """
#     创建MCP工具列表
#
#     从MCP服务器获取可用工具并转换为LangChain工具格式。
#
#     Args:
#         config: Agent配置
#
#     Returns:
#         Sequence[BaseTool]: MCP工具列表
#     """
#     # 注意：MCP工具需要在运行时通过MultiServerMCPClient获取
#     # 这里返回空列表，实际工具在create_api_test_agent中通过MCP客户端加载
#     return []

# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkU1SllRPT06OWYzODVhMDU=

def create_llm(config: AgentConfig) -> ChatOpenAI:
    """
    创建LLM实例
    
    Args:
        config: Agent配置
        
    Returns:
        ChatOpenAI: LLM实例
    """
    return ChatOpenAI(
        model=config.llm.model_name,
        api_key=config.llm.api_key,
        base_url=config.llm.api_base,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
    )


def create_api_test_agent(
    config: Optional[AgentConfig] = None,
    tools: Optional[Sequence[BaseTool]] = None,
    subagents: Optional[Sequence[SubAgent]] = None,
    system_prompt: Optional[str] = None,
    debug: bool = False,
) -> CompiledStateGraph:
    """
    创建API测试Agent
    
    基于DeepAgents框架创建一个完整的API测试编排Agent。
    该Agent可以协调多个专业子Agent完成API测试任务。
    
    Args:
        config: Agent配置，如果为None则使用默认配置
        tools: 额外的工具列表，会与MCP工具合并
        subagents: 自定义子Agent列表，如果为None则使用默认子Agent
        system_prompt: 自定义系统提示词
        debug: 是否启用调试模式
        
    Returns:
        CompiledStateGraph: 编译后的Agent图
        
    Example:
        >>> from api_agent.core import create_api_test_agent
        >>> agent = create_api_test_agent()
        >>> result = agent.invoke({
        ...     "messages": [{"role": "user", "content": "分析这个API文档并生成测试计划"}]
        ... })
    """
    # 获取配置
    if config is None:
        config = get_config()
    
    # 创建LLM
    llm = create_llm(config)
    
    # 获取子Agent
    if subagents is None:
        subagents = list(get_all_subagents())
    
    # 合并工具
    all_tools = list(tools) if tools else []
    
    # 获取系统提示词
    prompt = system_prompt or ORCHESTRATOR_SYSTEM_PROMPT

    # 配置文件系统后端
    # 使用 FilesystemBackend 并启用 virtual_mode
    # 这样 agent 使用虚拟路径 (如 /test_outputs/xxx.py) 映射到实际文件系统
    output_dir = Path(config.test_execution.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    backend = FilesystemBackend(root_dir=output_dir, virtual_mode=True)

    # 添加输出目录信息到提示词（使用虚拟路径）
    prompt += f"\n\n## 工作目录\n测试输出目录: / (虚拟路径，映射到实际目录: {output_dir})"
    prompt += "\n注意：所有文件路径都使用虚拟路径格式，如 /test_file.py，不要使用 Windows 绝对路径。"

    logger.info(f"Creating API Test Agent with model: {config.llm.model_name}")
    logger.info(f"Backend root_dir: {output_dir}")
    logger.info(f"Subagents: {[sa['name'] for sa in subagents]}")
    logger.info(f"Tools: {len(all_tools)}")

    @before_model
    def normalize_tool_message_content(state: AgentState, runtime: Runtime):
        """
        规范化 ToolMessage 的 content 格式。

        某些 LLM API（如 DeepSeek）不支持内容块列表格式，只接受纯字符串。
        此中间件会将 ToolMessage 的 content 从列表格式转换为字符串格式。

        例如：
            content=[{'type': 'text', 'text': '...'}]
        转换为：
            content='...'
        """
        from langchain_core.messages import ToolMessage

        messages = state.get("messages", [])
        modified = False
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkU1SllRPT06OWYzODVhMDU=

        for i, msg in enumerate(messages):
            if isinstance(msg, ToolMessage):
                content = msg.content
                # 如果 content 是列表格式，将其转换为字符串
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            # 处理 {'type': 'text', 'text': '...'} 格式
                            if item.get('type') == 'text' and 'text' in item:
                                text_parts.append(item['text'])
                            else:
                                # 其他字典格式，转换为字符串
                                text_parts.append(str(item))
                        elif hasattr(item, 'text'):
                            # 处理对象格式
                            text_parts.append(str(item.text))
                        else:
                            text_parts.append(str(item))

                    # 合并为单个字符串
                    merged_content = "\n".join(text_parts)

                    # 创建新的 ToolMessage，保持其他属性不变
                    messages[i] = ToolMessage(
                        content=merged_content,
                        tool_call_id=msg.tool_call_id,
                        name=getattr(msg, 'name', None),
                        id=msg.id,
                    )
                    modified = True

        if modified:
            logger.debug(f"Normalized {sum(1 for m in messages if isinstance(m, ToolMessage))} ToolMessage content(s) to string format")

        return {"messages": messages} if modified else None

    @before_model
    def test_before_model(state: AgentState, runtime: Runtime):
        print(state)
    # 创建DeepAgent
    agent = create_deep_agent(
        model=llm,
        tools=all_tools,
        middleware=[normalize_tool_message_content],
        system_prompt=prompt,
        subagents=subagents,
        backend=backend,
        debug=debug,
        name="api-test-orchestrator",
    )
    
    return agent
#
#
# async def create_api_test_agent_with_mcp(
#     config: Optional[AgentConfig] = None,
#     additional_tools: Optional[Sequence[BaseTool]] = None,
#     subagents: Optional[Sequence[SubAgent]] = None,
#     system_prompt: Optional[str] = None,
#     debug: bool = False,
# ) -> CompiledStateGraph:
#     """
#     创建带MCP工具的API测试Agent（异步版本）
#
#     此函数会连接到MCP服务器并获取可用工具。
#
#     Args:
#         config: Agent配置
#         additional_tools: 额外的工具列表
#         subagents: 自定义子Agent列表
#         system_prompt: 自定义系统提示词
#         debug: 是否启用调试模式
#
#     Returns:
#         CompiledStateGraph: 编译后的Agent图
#     """
#     from langchain_mcp_adapters.client import MultiServerMCPClient
#
#     # 获取配置
#     if config is None:
#         config = get_config()
#
#     # 配置MCP服务器
#     mcp_servers = {
#         "pytest_generator": {
#             "url": config.mcp_servers.pytest_generator_url,
#             "transport": "sse",
#         },
#         "test_executor": {
#             "url": config.mcp_servers.test_executor_url,
#             "transport": "sse",
#         },
#         "rag_server": {
#             "url": config.mcp_servers.rag_server_url,
#             "transport": "sse",
#         },
#     }
#
#     # 创建MCP客户端并获取工具
#     # 使用拦截器规范化内容格式，确保 DeepSeek API 兼容性
#     # content_normalizer = ContentNormalizerInterceptor()
#     async with MultiServerMCPClient(
#         mcp_servers,
#         # tool_interceptors=[content_normalizer]
#     ) as client:
#         mcp_tools = asyncio.run(client.get_tools())
#         logger.info(f"Loaded {len(mcp_tools)} MCP tools")
#
#         # 合并工具
#         all_tools = list(mcp_tools)
#         if additional_tools:
#             all_tools.extend(additional_tools)
#
#         # 创建Agent
#         agent = create_api_test_agent(
#             config=config,
#             tools=all_tools,
#             subagents=subagents,
#             system_prompt=system_prompt,
#             debug=debug,
#         )
#
#         return agent


class APITestOrchestrator:
    """
    API测试编排器类
    
    提供更高级的API测试编排功能，包括：
    - 会话管理
    - 状态持久化
    - 批量任务处理
    
    Attributes:
        config: Agent配置
        agent: 编译后的Agent图
        session_id: 当前会话ID
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        debug: bool = False,
    ):
        """
        初始化编排器
        
        Args:
            config: Agent配置
            debug: 是否启用调试模式
        """
        self.config = config or get_config()
        self.debug = debug
        self.agent: Optional[CompiledStateGraph] = None
        self.session_id: Optional[str] = None
        self._mcp_client = None
    
    async def initialize(self) -> None:
        """
        异步初始化编排器
        
        连接MCP服务器并创建Agent。
        """
        from langchain_mcp_adapters.client import MultiServerMCPClient
        import uuid
        
        # 生成会话ID
        self.session_id = str(uuid.uuid4())
        
        # 配置MCP服务器（使用统一的 mcp_settings）
        from config.mcp_settings import mcp_settings
        
        mcp_servers = {}
        
        # Pytest MCP 服务（合并了 pytest_generator 和 test_executor）
        if mcp_settings.pytest_mcp_enabled:
            mcp_servers["pytest-mcp"] = mcp_settings.get_pytest_mcp_config()
        
        # RAG Query MCP 服务
        if mcp_settings.rag_query_enabled:
            mcp_servers["rag-query-mcp"] = mcp_settings.get_rag_query_config()
        
        # 创建MCP客户端，使用拦截器规范化内容格式
        # DeepSeek API 不支持内容块列表格式，需要将其转换为纯字符串
        # content_normalizer = ContentNormalizerInterceptor()
        self._mcp_client = MultiServerMCPClient(
            mcp_servers,
            # tool_interceptors=[content_normalizer]
        )

        # 获取MCP工具
        mcp_tools = await self._mcp_client.get_tools()
        logger.info(f"Loaded {len(mcp_tools)} MCP tools for session {self.session_id}")
        
        # 创建Agent
        self.agent = create_api_test_agent(
            config=self.config,
            tools=mcp_tools,
            debug=self.debug,
        )
        
        logger.info(f"APITestOrchestrator initialized with session {self.session_id}")
    
    async def close(self) -> None:
        """关闭编排器，释放资源"""
        if self._mcp_client:
            await self._mcp_client.__aexit__(None, None, None)
            self._mcp_client = None
        self.agent = None
        logger.info(f"APITestOrchestrator closed for session {self.session_id}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def run(self, message: str) -> dict[str, Any]:
        """
        运行Agent处理用户消息
        
        Args:
            message: 用户消息
            
        Returns:
            dict: Agent响应
        """
        if self.agent is None:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": message}]
        })
        
        return result
    
    async def stream(self, message: str):
        """
        流式运行Agent处理用户消息
        
        Args:
            message: 用户消息
            
        Yields:
            Agent响应片段
        """
        if self.agent is None:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkU1SllRPT06OWYzODVhMDU=
        
        async for chunk in self.agent.astream({
            "messages": [{"role": "user", "content": message}]
        }):
            yield chunk

