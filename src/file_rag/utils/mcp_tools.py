"""
MCP 工具加载模块
负责加载和管理 MCP (Model Context Protocol) 工具
"""


async def get_mcp_tools_from_config() -> list:
    """
    从配置文件加载 MCP 工具（可选）- 异步版本

    如果 MCP 服务不可用，会返回空列表，不影响主功能

    Returns:
        工具列表，如果加载失败则返回空列表
    """
    try:
        # 导入配置
        from file_rag.mcp_config import get_enabled_mcp_servers, is_mcp_enabled, MCP_SETTINGS

        # 检查全局开关
        if not is_mcp_enabled():
            print("[MCP] MCP 功能已在配置中禁用")
            return []

        # 获取启用的服务
        enabled_servers = get_enabled_mcp_servers()
        if not enabled_servers:
            print("[MCP] 没有启用的 MCP 服务")
            return []

        # 尝试导入 MCP 客户端
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
        except ImportError:
            print("[MCP] ⚠️ langchain-mcp-adapters 未安装，跳过 MCP 工具加载")
            print("[MCP] 提示：运行 'pip install langchain-mcp-adapters' 来启用 MCP 功能")
            return []

        # 准备服务器配置（移除 enabled 和 description 字段）
        server_configs = {}
        for name, config in enabled_servers.items():
            server_config = {k: v for k, v in config.items() if k not in ['enabled', 'description']}
            server_configs[name] = server_config
            print(f"[MCP] 正在连接 {name} ({config.get('description', 'MCP服务')})...")

        # 创建客户端并获取工具
        try:
            client = MultiServerMCPClient(server_configs)
            tools = await client.get_tools()  # 使用 await 而不是 asyncio.run

            if tools:
                print(f"[MCP] ✓ 成功加载 {len(tools)} 个 MCP 工具")
                for tool in tools:
                    print(f"[MCP]   - {tool.name}: {tool.description[:50]}...")
            else:
                print("[MCP] ⚠️ 未获取到任何工具")

            return tools

        except Exception as client_error:
            import traceback
            print(f"[MCP] ⚠️ MCP 客户端连接失败: {client_error}")
            print(f"[MCP] 详细错误信息:")
            traceback.print_exc()
            print(f"[MCP] 提示：请确保 Chrome MCP 服务正在运行（http://127.0.0.1:12306/mcp）")
            return []

    except Exception as e:
        import traceback
        print(f"[MCP] ⚠️ 加载 MCP 工具失败: {e}")
        print(f"[MCP] 详细错误信息:")
        traceback.print_exc()
        from file_rag.mcp_config import MCP_SETTINGS
        if not MCP_SETTINGS.get("fail_silently", True):
            raise
        print("[MCP] 系统将继续运行，不影响其他功能")
        return []


async def get_all_mcp_tools() -> list:
    """
    加载所有可用的 MCP 工具（可选）- 异步版本

    这是主要的 MCP 工具加载入口

    Returns:
        所有 MCP 工具的列表
    """
    all_tools = []

    # 从配置文件加载 MCP 工具
    mcp_tools = await get_mcp_tools_from_config()
    all_tools.extend(mcp_tools)

    if all_tools:
        print(f"[MCP] 总共加载了 {len(all_tools)} 个 MCP 工具")
    else:
        print("[MCP] 未加载任何 MCP 工具，使用默认功能")

    return all_tools


async def get_chart_mcp_tools() -> list:
    """
    单独加载图表 MCP 工具

    Returns:
        图表 MCP 工具列表，如果加载失败则返回空列表
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        # 只加载图表 MCP 服务
        chart_config = {
            "chart_mcp": {
                "command": "npx",
                "args": ["-y", "@antv/mcp-server-chart"],
                "transport": "stdio",
            }
        }

        print("[Chart MCP] 正在加载图表生成工具...")
        client = MultiServerMCPClient(chart_config)
        tools = await client.get_tools()

        if tools:
            print(f"[Chart MCP] ✓ 成功加载 {len(tools)} 个图表工具")
            for tool in tools:
                print(f"[Chart MCP]   - {tool.name}")
        else:
            print("[Chart MCP] ⚠️ 未获取到图表工具")

        return tools
    except Exception as e:
        print(f"[Chart MCP] ⚠️ 加载图表工具失败: {e}")
        return []

