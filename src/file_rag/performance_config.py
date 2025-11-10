"""
性能优化配置模块
用于控制自动化测试的性能相关参数
"""

# 性能优化配置
PERFORMANCE_CONFIG = {
    # 图表生成
    "enable_chart_by_default": False,  # 默认不生成图表（节省 5-10 秒）
    
    # Agent 配置
    "recursion_limit": 30,  # Agent 递归限制（从 50 降到 30，节省 20-30%）
    "max_tool_calls": 25,  # 最大工具调用次数
    
    # 超时配置
    "agent_timeout": 60,  # Agent 执行超时（秒）
    "tool_timeout": 10,  # 单个工具调用超时（秒）
    
    # 执行模式
    "fast_mode": True,  # 快速模式：简化提示词，减少验证步骤
    "verbose": True,  # 是否输出详细日志
    
    # 报告生成
    "generate_detailed_report": True,  # 是否生成详细报告
    "include_screenshots": False,  # 是否包含截图（暂未实现）
}

# 快速模式配置（最快速度）
FAST_MODE_CONFIG = {
    "enable_chart_by_default": False,
    "recursion_limit": 20,  # 进一步降低
    "max_tool_calls": 15,
    "agent_timeout": 45,
    "tool_timeout": 8,
    "fast_mode": True,
    "verbose": False,  # 减少日志输出
    "generate_detailed_report": False,  # 只生成简要报告
    "include_screenshots": False,
}

# 标准模式配置（平衡速度和质量）
STANDARD_MODE_CONFIG = {
    "enable_chart_by_default": False,
    "recursion_limit": 30,
    "max_tool_calls": 25,
    "agent_timeout": 60,
    "tool_timeout": 10,
    "fast_mode": True,
    "verbose": True,
    "generate_detailed_report": True,
    "include_screenshots": False,
}

# 完整模式配置（最高质量，最慢）
FULL_MODE_CONFIG = {
    "enable_chart_by_default": True,  # 生成图表
    "recursion_limit": 50,
    "max_tool_calls": 40,
    "agent_timeout": 120,
    "tool_timeout": 15,
    "fast_mode": False,
    "verbose": True,
    "generate_detailed_report": True,
    "include_screenshots": True,
}

# 当前使用的配置（默认使用标准模式）
CURRENT_CONFIG = STANDARD_MODE_CONFIG


def get_performance_config(mode: str = "standard") -> dict:
    """
    获取性能配置
    
    Args:
        mode: 模式名称 ("fast", "standard", "full")
    
    Returns:
        配置字典
    """
    if mode == "fast":
        return FAST_MODE_CONFIG
    elif mode == "standard":
        return STANDARD_MODE_CONFIG
    elif mode == "full":
        return FULL_MODE_CONFIG
    else:
        return STANDARD_MODE_CONFIG


def set_performance_mode(mode: str):
    """
    设置性能模式
    
    Args:
        mode: 模式名称 ("fast", "standard", "full")
    """
    global CURRENT_CONFIG
    CURRENT_CONFIG = get_performance_config(mode)
    print(f"[性能配置] 已切换到 {mode} 模式")
    print(f"  - 递归限制: {CURRENT_CONFIG['recursion_limit']}")
    print(f"  - 生成图表: {CURRENT_CONFIG['enable_chart_by_default']}")
    print(f"  - 快速模式: {CURRENT_CONFIG['fast_mode']}")


# 使用示例
if __name__ == "__main__":
    print("性能配置模块")
    print("="*60)
    
    print("\n快速模式配置:")
    for key, value in FAST_MODE_CONFIG.items():
        print(f"  {key}: {value}")
    
    print("\n标准模式配置:")
    for key, value in STANDARD_MODE_CONFIG.items():
        print(f"  {key}: {value}")
    
    print("\n完整模式配置:")
    for key, value in FULL_MODE_CONFIG.items():
        print(f"  {key}: {value}")
    
    print("\n当前配置:")
    for key, value in CURRENT_CONFIG.items():
        print(f"  {key}: {value}")

