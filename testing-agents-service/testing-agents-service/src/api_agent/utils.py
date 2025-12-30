"""
API Agent工具模块

提供通用工具函数、日志配置和辅助功能。
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import os
import re
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from functools import wraps
import asyncio

from .core.config import get_config, LoggingConfig

# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0ZjMFpRPT06ZTU5NzkyY2M=

# ============================================================================
# 日志配置
# ============================================================================

def setup_logging(config: Optional[LoggingConfig] = None) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        config: 日志配置，如果为None则使用默认配置
        
    Returns:
        配置好的logger实例
    """
    if config is None:
        config = get_config().logging
    
    logger = logging.getLogger("api_agent")
    logger.setLevel(getattr(logging, config.level))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    formatter = logging.Formatter(config.format)
    
    # 控制台输出
    if config.console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件输出
    if config.file_path:
        file_path = Path(config.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(file_path), encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "api_agent") -> logging.Logger:
    """获取logger实例"""
    return logging.getLogger(name)


# ============================================================================
# 字符串处理
# ============================================================================

def sanitize_name(name: str, max_length: int = 50) -> str:
    """
    清理名称，使其适合作为Python标识符
    
    Args:
        name: 原始名称
        max_length: 最大长度
        
    Returns:
        清理后的名称
    """
    # 移除非字母数字字符
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # 确保不以数字开头
    if sanitized and sanitized[0].isdigit():
        sanitized = f"test_{sanitized}"
    # 移除连续下划线
    sanitized = re.sub(r'_+', '_', sanitized)
    # 移除首尾下划线
    sanitized = sanitized.strip('_')
    # 限制长度
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    # 确保非空
    return sanitized or "unnamed"


def to_snake_case(name: str) -> str:
    """
    转换为snake_case格式
    
    Args:
        name: 原始名称
        
    Returns:
        snake_case格式的名称
    """
    # 在大写字母前插入下划线
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 在小写字母和大写字母之间插入下划线
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def to_camel_case(name: str) -> str:
    """
    转换为camelCase格式
    
    Args:
        name: 原始名称（snake_case）
        
    Returns:
        camelCase格式的名称
    """
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
# pragma: no cover  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0ZjMFpRPT06ZTU5NzkyY2M=


def generate_test_id(endpoint: str, method: str, description: str = "") -> str:
    """
    生成唯一的测试ID
    
    Args:
        endpoint: API端点
        method: HTTP方法
        description: 测试描述
        
    Returns:
        唯一的测试ID
    """
    content = f"{method}:{endpoint}:{description}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"test_{sanitize_name(method.lower())}_{sanitize_name(endpoint)}_{hash_value}"


# ============================================================================
# 文件操作
# ============================================================================

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_file(
    path: Union[str, Path],
    content: str,
    encoding: str = "utf-8"
) -> Path:
    """
    安全写入文件
    
    Args:
        path: 文件路径
        content: 文件内容
        encoding: 编码格式
        
    Returns:
        写入的文件路径
    """
    path = Path(path)
    ensure_directory(path.parent)
    path.write_text(content, encoding=encoding)
    return path


def safe_read_file(
    path: Union[str, Path],
    encoding: str = "utf-8",
    default: str = ""
) -> str:
    """
    安全读取文件
    
    Args:
        path: 文件路径
        encoding: 编码格式
        default: 文件不存在时的默认值
        
    Returns:
        文件内容
    """
    path = Path(path)
    if path.exists():
        return path.read_text(encoding=encoding)
    return default


def load_json_file(path: Union[str, Path]) -> Dict[str, Any]:
    """
    加载JSON文件
    
    Args:
        path: 文件路径
        
    Returns:
        解析后的JSON对象
    """
    content = safe_read_file(path)
    if content:
        return json.loads(content)
    return {}


def save_json_file(
    path: Union[str, Path],
    data: Any,
    indent: int = 2
) -> Path:
    """
    保存JSON文件
    
    Args:
        path: 文件路径
        data: 要保存的数据
        indent: 缩进空格数
        
    Returns:
        保存的文件路径
    """
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    return safe_write_file(path, content)
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0ZjMFpRPT06ZTU5NzkyY2M=


# ============================================================================
# 时间处理
# ============================================================================

def get_timestamp() -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_iso_timestamp() -> str:
    """获取ISO格式时间戳"""
    return datetime.now().isoformat()


def format_duration(seconds: float) -> str:
    """
    格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


# ============================================================================
# 异步工具
# ============================================================================

def async_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    异步重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍增因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger = get_logger()
                        logger.warning(
                            f"重试 {func.__name__} (尝试 {attempt + 1}/{max_retries}): {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        return wrapper
    return decorator
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0ZjMFpRPT06ZTU5NzkyY2M=


async def run_with_timeout(
    coro,
    timeout: float,
    timeout_message: str = "操作超时"
):
    """
    带超时的异步执行
    
    Args:
        coro: 协程
        timeout: 超时时间（秒）
        timeout_message: 超时错误消息
        
    Returns:
        协程执行结果
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(timeout_message)


# ============================================================================
# 数据处理
# ============================================================================

def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    深度合并两个字典
    
    Args:
        base: 基础字典
        override: 覆盖字典
        
    Returns:
        合并后的字典
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def flatten_dict(
    d: Dict,
    parent_key: str = "",
    sep: str = "."
) -> Dict[str, Any]:
    """
    扁平化嵌套字典
    
    Args:
        d: 嵌套字典
        parent_key: 父键前缀
        sep: 分隔符
        
    Returns:
        扁平化的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取JSON对象
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        提取的JSON对象，如果未找到则返回None
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试从代码块中提取
    json_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*\}'
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None

