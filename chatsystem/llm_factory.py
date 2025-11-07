"""
LLM 工厂模块
用于创建和管理 LLM 实例
"""

import logging
import os
from typing import Optional, Dict, Any

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM 工厂类"""
    
    # 缓存 LLM 实例
    _instances: Dict[str, ChatOpenAI] = {}
    
    # 默认配置
    DEFAULT_CONFIG = {
        "temperature": 0.7,
        "max_tokens": 2000,
        "request_timeout": 60.0,
        "max_retries": 3,
    }
    
    # 模型配置
    MODEL_CONFIG = {
        "gpt-4o": {
            "model_name": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "deepseek-chat": {
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "doubao": {
            "model_name": "doubao",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "qwen": {
            "model_name": "qwen",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
    }
    
    @classmethod
    def create_llm(
        cls,
        model: str = "gpt-4o",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatOpenAI:
        """
        创建 LLM 实例
        
        参数:
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数
        
        返回:
            ChatOpenAI 实例
        """
        # 检查缓存
        cache_key = f"{model}_{temperature}_{max_tokens}"
        if cache_key in cls._instances:
            logger.debug(f"使用缓存的 LLM 实例: {cache_key}")
            return cls._instances[cache_key]
        
        # 获取模型配置
        model_config = cls.MODEL_CONFIG.get(model, {})
        config = {**cls.DEFAULT_CONFIG, **model_config}
        
        # 覆盖参数
        if temperature is not None:
            config["temperature"] = temperature
        if max_tokens is not None:
            config["max_tokens"] = max_tokens
        
        # 合并额外参数
        config.update(kwargs)
        
        # 获取 API 配置
        api_key = os.getenv("ONE_API_KEY")
        api_base = os.getenv("ONE_API_BASE_URL")
        
        if not api_key:
            raise ValueError("ONE_API_KEY 环境变量未设置")
        
        # 创建 LLM 实例
        logger.info(f"创建 LLM 实例: {model}")
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=api_base,
            **config
        )
        
        # 缓存实例
        cls._instances[cache_key] = llm
        
        return llm
    
    @classmethod
    def get_llm(cls, model: str = "gpt-4o") -> ChatOpenAI:
        """获取 LLM 实例（使用默认配置）"""
        return cls.create_llm(model)
    
    @classmethod
    def clear_cache(cls):
        """清除缓存"""
        cls._instances.clear()
        logger.info("LLM 实例缓存已清除")


# 便捷函数
def create_llm(
    model: str = "gpt-4o",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatOpenAI:
    """创建 LLM 实例的便捷函数"""
    return LLMFactory.create_llm(model, temperature, max_tokens, **kwargs)


def get_llm(model: str = "gpt-4o") -> ChatOpenAI:
    """获取 LLM 实例的便捷函数"""
    return LLMFactory.get_llm(model)

