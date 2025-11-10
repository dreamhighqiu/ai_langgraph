"""
MCP 配置文件
用于配置各种 MCP 服务的连接信息
"""

# MCP 服务配置
MCP_SERVERS = {
    # Chrome MCP 服务
    "chrome_mcp": {
        "enabled": True,  # 是否启用
        "url": "http://127.0.0.1:12306/mcp",
        "transport": "streamable_http",
        "description": "Chrome 浏览器自动化工具"
    },

    # Chart MCP 服务（图表生成）
    "chart_mcp": {
        "enabled": True,  # 是否启用
        "command": "npx",
        "args": ["-y", "@antv/mcp-server-chart"],
        "transport": "stdio",
        "description": "图表生成工具（支持柱状图、折线图、饼图等）"
    },

    # 可以添加更多 MCP 服务
    # 例如：文件系统 MCP
    # "filesystem_mcp": {
    #     "enabled": False,
    #     "command": "npx",
    #     "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
    #     "transport": "stdio",
    #     "description": "文件系统操作工具"
    # },

    # 例如：GitHub MCP
    # "github_mcp": {
    #     "enabled": False,
    #     "command": "npx",
    #     "args": ["-y", "@modelcontextprotocol/server-github"],
    #     "transport": "stdio",
    #     "env": {
    #         "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    #     },
    #     "description": "GitHub 操作工具"
    # },
}

# 全局 MCP 设置
MCP_SETTINGS = {
    "enable_mcp": True,  # 全局开关，是否启用 MCP 功能
    "timeout": 30,  # 连接超时时间（秒）
    "retry_count": 3,  # 连接失败重试次数
    "fail_silently": True,  # 如果 MCP 加载失败，是否静默失败（不影响主功能）
}

# 获取所有启用的 MCP 服务
def get_enabled_mcp_servers():
    """
    获取所有启用的 MCP 服务配置
    
    Returns:
        启用的 MCP 服务配置字典
    """
    return {
        name: config 
        for name, config in MCP_SERVERS.items() 
        if config.get("enabled", False)
    }

# 检查 MCP 功能是否全局启用
def is_mcp_enabled():
    """
    检查 MCP 功能是否全局启用
    
    Returns:
        bool: MCP 是否启用
    """
    return MCP_SETTINGS.get("enable_mcp", True)

