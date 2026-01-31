"""
LLM 配置管理模块

提供统一的 LLM 初始化和配置管理，避免在每个 agent 中重复配置。

使用方式：
    from config.llm_config import get_default_llm, get_llm
    
    # 获取默认 LLM
    model = get_default_llm()
    
    # 获取指定提供商的 LLM
    model = get_llm(provider="openai", model_name="gpt-4o")
"""

from typing import Optional, Literal
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from config.settings import settings

LLMProvider = Literal["openai", "deepseek", "anthropic"]


def get_llm(
    provider: Optional[LLMProvider] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    **kwargs
) -> BaseChatModel:
    """
    获取配置好的 LLM 实例
    
    Args:
        provider: LLM 提供商（openai, deepseek, anthropic）
                 如果为 None，使用 settings.default_llm_provider
        model_name: 模型名称，如果为 None，使用对应提供商的默认模型
        temperature: 温度参数，默认 0.0（确定性输出）
        **kwargs: 传递给 init_chat_model 的其他参数
    
    Returns:
        BaseChatModel: 初始化好的 LLM 实例
    
    Examples:
        >>> # 使用默认配置
        >>> model = get_llm()
        
        >>> # 指定提供商和模型
        >>> model = get_llm(provider="openai", model_name="gpt-4o")
        
        >>> # 使用 DeepSeek
        >>> model = get_llm(provider="deepseek")
    """
    # 确定使用的提供商
    if provider is None:
        provider = settings.default_llm_provider
    
    # 根据提供商配置 LLM
    if provider == "openai":
        model_name = model_name or settings.openai_model
        
        # 配置参数
        config_kwargs = {
            "temperature": temperature,
            **kwargs
        }
        
        # 如果配置了自定义 base_url，添加到配置中
        if settings.openai_base_url:
            config_kwargs["base_url"] = settings.openai_base_url
        
        return init_chat_model(
            f"openai:{model_name}",
            **config_kwargs
        )
    
    elif provider == "deepseek":
        model_name = model_name or settings.deepseek_model
        
        # 配置参数
        config_kwargs = {
            "temperature": temperature,
            **kwargs
        }
        
        # 如果配置了自定义 base_url，添加到配置中
        if settings.deepseek_base_url:
            config_kwargs["base_url"] = settings.deepseek_base_url
        
        return init_chat_model(
            f"deepseek:{model_name}",
            **config_kwargs
        )
    
    elif provider == "anthropic":
        model_name = model_name or settings.anthropic_model
        return init_chat_model(
            f"anthropic:{model_name}",
            temperature=temperature,
            **kwargs
        )
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, deepseek, anthropic"
        )


def get_default_llm(temperature: float = 0.0, **kwargs) -> BaseChatModel:
    """
    获取默认配置的 LLM 实例
    
    使用 settings.default_llm_provider 指定的提供商和对应的默认模型。
    
    Args:
        temperature: 温度参数，默认 0.0（确定性输出）
        **kwargs: 传递给 init_chat_model 的其他参数
    
    Returns:
        BaseChatModel: 初始化好的 LLM 实例
    
    Examples:
        >>> model = get_default_llm()
        >>> model = get_default_llm(temperature=0.7)
    """
    return get_llm(
        provider=settings.default_llm_provider,
        temperature=temperature,
        **kwargs
    )


def get_llm_info() -> dict:
    """
    获取当前 LLM 配置信息（用于日志和调试）
    
    Returns:
        dict: LLM 配置信息
    
    Examples:
        >>> info = get_llm_info()
        >>> print(f"Using {info['provider']} with model {info['model']}")
    """
    provider = settings.default_llm_provider
    
    if provider == "openai":
        return {
            "provider": "openai",
            "model": settings.openai_model,
            "base_url": settings.openai_base_url or "https://api.openai.com/v1",
            "api_key_configured": bool(settings.openai_api_key)
        }
    elif provider == "deepseek":
        return {
            "provider": "deepseek",
            "model": settings.deepseek_model,
            "api_key_configured": bool(settings.deepseek_api_key)
        }
    elif provider == "anthropic":
        return {
            "provider": "anthropic",
            "model": settings.anthropic_model,
            "api_key_configured": bool(settings.anthropic_api_key)
        }
    else:
        return {
            "provider": provider,
            "error": "Unknown provider"
        }


# 便捷函数：直接导出默认 model 实例（向后兼容）
def init_default_model() -> BaseChatModel:
    """
    初始化默认模型（向后兼容旧代码）
    
    Returns:
        BaseChatModel: 默认 LLM 实例
    """
    return get_default_llm()


def get_llm_model(temperature: float = 0.0, **kwargs) -> BaseChatModel:
    """
    获取 LLM 模型实例（get_default_llm 的别名，向后兼容）
    
    Args:
        temperature: 温度参数，默认 0.0（确定性输出）
        **kwargs: 传递给 init_chat_model 的其他参数
    
    Returns:
        BaseChatModel: 初始化好的 LLM 实例
    
    Examples:
        >>> model = get_llm_model()
        >>> model = get_llm_model(temperature=0.7)
    """
    return get_default_llm(temperature=temperature, **kwargs)
