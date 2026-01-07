"""K6性能测试智能体 - 主入口."""



import os
from pathlib import Path
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VERWa1ZBPT06YmFiMTMxNzQ=

from deepagents import create_deep_agent, SubAgent
from deepagents.backends import FilesystemBackend
from k6_agent.config import K6Config, DEFAULT_CONFIG
from k6_agent.prompts import SYSTEM_PROMPT
from k6_agent.subagents import create_all_subagents
from k6_agent.tools.mcp import get_rag_tools, get_chart_tools, get_login_tools
from k6_agent.tools.executor import create_k6_executor_tool, create_script_save_tool
from k6_agent.tasks import create_task_tools, get_task_manager


def create_k6_agent(
    model: str | BaseChatModel | None = None,
    *,
    config: K6Config | None = None,
    **kwargs: Any,
) -> CompiledStateGraph:
    """创建K6性能测试智能体.
    
    这是K6性能测试智能体平台的唯一入口。
    
    Args:
        model: 语言模型，可以是模型名称字符串或BaseChatModel实例
               默认使用 deepseek:deepseek-chat
        config: K6配置，默认使用DEFAULT_CONFIG
        **kwargs: 传递给create_deep_agent的额外参数
        
    Returns:
        编译后的智能体（CompiledStateGraph）
        
    Example:
        ```python
        import os
        from k6_agent import create_k6_agent
        
        # 设置API密钥
        os.environ["DEEPSEEK_API_KEY"] = "your-api-key"
        
        # 创建智能体
        agent = create_k6_agent()
        
        # 使用智能体
        result = agent.invoke({
            "messages": [
                {"role": "user", "content": "请对登录接口进行性能测试"}
            ]
        })
        ```
    """
    cfg = config or DEFAULT_CONFIG
    os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"
    # 初始化语言模型
    if model is None:
        llm = init_chat_model("deepseek:deepseek-chat")
    elif isinstance(model, str):
        llm = init_chat_model(model)
    else:
        llm = model
    
    # 获取MCP工具
    rag_tools = get_rag_tools(cfg)
    chart_tools = get_chart_tools(cfg)
    # 可选工具
    login_tool = get_login_tools(cfg)

    # 创建执行工具
    executor_tool = create_k6_executor_tool(cfg)
    script_save_tool = create_script_save_tool(cfg)
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VERWa1ZBPT06YmFiMTMxNzQ=

    # 创建任务管理工具（异步执行 + 状态监控）
    task_tools = create_task_tools(cfg)
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VERWa1ZBPT06YmFiMTMxNzQ=


    # 主智能体工具（脚本保存、执行、任务管理）
    main_tools = [script_save_tool, executor_tool] + task_tools

    # 创建子智能体
    subagents = create_all_subagents(
        rag_tools=rag_tools,
        chart_tools=chart_tools,
        script_tools=[script_save_tool] + login_tool,
        analyzer_tools=task_tools,  # 分析智能体可查询任务结果
        model=llm,
    )
    
    # 配置文件系统后端
    # 使用 FilesystemBackend 并启用 virtual_mode
    # 这样 agent 使用虚拟路径 (如 /k6_scripts/test.js) 映射到实际文件系统
    workspace_root = Path(cfg.workspace_root).resolve()
    backend = FilesystemBackend(root_dir=workspace_root, virtual_mode=True)

    # 创建主智能体
    agent = create_deep_agent(
        model=llm,
        tools=main_tools,
        system_prompt=SYSTEM_PROMPT,
        subagents=subagents,
        backend=backend,
        **kwargs,
    ).with_config(RunnableConfig(recursion_limit=1000))
# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VERWa1ZBPT06YmFiMTMxNzQ=

    return agent

