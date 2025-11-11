"""
企业级 LLM 封装模块
提供统一的大模型调用接口,支持 one-api 集成
"""

import os
from pathlib import Path
from typing import Optional, List
from enum import Enum
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

# 加载环境变量 - 从项目根目录加载 .env 文件
# 确保无论从哪个目录运行，都能正确加载 .env 文件
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    # 如果找不到 .env 文件，尝试从当前工作目录加载
    load_dotenv()


class ModelType(str, Enum):
    """模型类型枚举"""
    # 通用对话模型
    GPT_4O = "gpt-4o"
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4O_REALY = "gpt-4o-realy"
    GPT_5 = "gpt-5"
    
    # DeepSeek 系列
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"
    DEEPSEEK_REASONER = "deepseek-reasoner"
    
    # 其他模型
    O3 = "o3"
    O4 = "o4-mini"
    
    # Embedding 模型
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


class LLMConfig:
    """LLM 配置类 - 统一管理所有配置"""
    
    # one-api 配置
    ONE_API_KEY = os.getenv("ONE_API_KEY", "sk-0DSjgogbOJdMmIBv476a4aF9431b4f15B70dC093Aa15A2Ac")
    ONE_API_BASE_URL = os.getenv("ONE_API_BASE_URL", "http://47.253.63.85:3000")
    
    # 默认模型
    # DEFAULT_MODEL = ModelType.GPT_4O
    DEFAULT_MODEL = ModelType.DEEPSEEK_CHAT
    
    # 默认参数
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TIMEOUT = 60
    DEFAULT_MAX_RETRIES = 3


class LLMFactory:
    """
    LLM 工厂类 - 企业级大模型封装
    
    核心功能:
    1. 统一的模型创建接口
    2. 自动配置管理
    3. 参数验证和默认值处理
    4. 支持多种模型快速切换
    
    使用示例:
        # 方式1: 使用默认配置(GPT-4O)
        llm = LLMFactory.create_llm()
        
        # 方式2: 指定模型
        llm = LLMFactory.create_llm(model=ModelType.DEEPSEEK_CHAT)
        
        # 方式3: 自定义参数
        llm = LLMFactory.create_llm(
            model=ModelType.GPT_4O,
            temperature=0.5,
            max_tokens=1000
        )
        
        # 方式4: 使用字符串指定模型
        llm = LLMFactory.create_llm(model="deepseek-chat")
    """
    
    @staticmethod
    def create_llm(
        model: Optional[str | ModelType] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        创建 LLM 实例
        
        Args:
            model: 模型类型,可以是 ModelType 枚举或字符串,默认使用 GPT_4O
            temperature: 温度参数 (0-1),控制输出随机性,默认 0.7
            max_tokens: 最大生成 token 数,默认 2000
            timeout: 请求超时时间(秒),默认 60
            max_retries: 最大重试次数,默认 3
            **kwargs: 其他参数传递给底层模型
        
        Returns:
            BaseChatModel: LLM 实例
        
        Raises:
            ValueError: 当模型名称不支持时
        """
        # 处理模型参数
        if model is None:
            model_name = LLMConfig.DEFAULT_MODEL.value
        elif isinstance(model, ModelType):
            model_name = model.value
        elif isinstance(model, str):
            # 验证模型是否支持
            if model not in LLMFactory.get_available_models():
                raise ValueError(
                    f"不支持的模型: {model}\n"
                    f"支持的模型: {', '.join(LLMFactory.get_available_models())}"
                )
            model_name = model
        else:
            raise ValueError(f"无效的模型类型: {type(model)}")
        
        # 使用默认值
        temperature = temperature if temperature is not None else LLMConfig.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or LLMConfig.DEFAULT_MAX_TOKENS
        timeout = timeout or LLMConfig.DEFAULT_TIMEOUT
        max_retries = max_retries or LLMConfig.DEFAULT_MAX_RETRIES
        
        # 创建 LLM 实例
        # 确保 base_url 包含 /v1 后缀
        base_url = LLMConfig.ONE_API_BASE_URL
        if not base_url.endswith('/v1'):
            base_url = base_url.rstrip('/') + '/v1'

        return ChatOpenAI(
            model=model_name,
            api_key=LLMConfig.ONE_API_KEY,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
    
    @staticmethod
    def get_available_models() -> List[str]:
        """
        获取所有可用的模型列表
        
        Returns:
            List[str]: 模型名称列表
        """
        return [model.value for model in ModelType]
    
    @staticmethod
    def print_available_models():
        """打印所有可用的模型"""
        print("=" * 60)
        print("可用模型列表:")
        print("=" * 60)
        
        # 按类别分组显示
        print("\n通用对话模型:")
        for model in [ModelType.GPT_4O, ModelType.GPT_4_1, ModelType.GPT_4_1_MINI, ModelType.GPT_4O_REALY]:
            print(f"  - {model.value}")
        
        print("\nDeepSeek 系列:")
        for model in [ModelType.DEEPSEEK_CHAT, ModelType.DEEPSEEK_CODER, ModelType.DEEPSEEK_REASONER]:
            print(f"  - {model.value}")
        
        print("\n其他模型:")
        for model in [ModelType.O3, ModelType.TEXT_EMBEDDING_3_LARGE]:
            print(f"  - {model.value}")
        
        print("=" * 60)


# ============================================================================
# 便捷函数 - 快速创建常用场景的 LLM
# ============================================================================

def create_llm(model: Optional[str | ModelType] = None, **kwargs) -> BaseChatModel:
    """
    快速创建 LLM 实例(推荐使用)
    
    Args:
        model: 模型类型,可以是 ModelType 枚举或字符串
        **kwargs: 其他参数
    
    Returns:
        BaseChatModel: LLM 实例
    
    Examples:
        >>> llm = create_llm()  # 使用默认模型
        >>> llm = create_llm("deepseek-chat")  # 使用字符串指定
        >>> llm = create_llm(ModelType.GPT_4O)  # 使用枚举指定
        >>> llm = create_llm("gpt-4o", temperature=0.5)  # 自定义参数
    """
    return LLMFactory.create_llm(model=model, **kwargs)


def create_chat_llm(**kwargs) -> BaseChatModel:
    """
    创建通用对话模型(使用 GPT-4O)
    适用于一般对话场景
    
    Args:
        **kwargs: 其他参数
    
    Returns:
        BaseChatModel: LLM 实例
    """
    return LLMFactory.create_llm(model=ModelType.GPT_4O, **kwargs)


def create_code_llm(**kwargs) -> BaseChatModel:
    """
    创建代码专用模型(使用 DeepSeek Coder)
    适用于代码生成、代码审查等场景
    
    Args:
        **kwargs: 其他参数
    
    Returns:
        BaseChatModel: LLM 实例
    """
    return LLMFactory.create_llm(
        model=ModelType.DEEPSEEK_CODER,
        temperature=0.2,  # 代码生成使用较低温度
        **kwargs
    )


def create_reasoning_llm(**kwargs) -> BaseChatModel:
    """
    创建推理专用模型(使用 DeepSeek Reasoner)
    适用于复杂推理、逻辑分析等场景
    
    Args:
        **kwargs: 其他参数
    
    Returns:
        BaseChatModel: LLM 实例
    """
    return LLMFactory.create_llm(
        model=ModelType.DEEPSEEK_REASONER,
        temperature=0.3,  # 推理使用较低温度
        **kwargs
    )


def create_fast_llm(**kwargs) -> BaseChatModel:
    """
    创建快速响应模型(使用 GPT-4.1-mini)
    适用于简单任务、快速响应场景
    
    Args:
        **kwargs: 其他参数
    
    Returns:
        BaseChatModel: LLM 实例
    """
    return LLMFactory.create_llm(
        model=ModelType.GPT_4_1_MINI,
        max_tokens=1000,  # 限制输出长度以提高速度
        **kwargs
    )


def create_gpt5_llm(**kwargs) -> BaseChatModel:
    """
    创建多模态模型(使用 GPT-5)
    适用于图片分析、PDF分析等多模态场景

    Args:
        **kwargs: 其他参数

    Returns:
        BaseChatModel: LLM 实例
    """
    return LLMFactory.create_llm(
        model=ModelType.GPT_5,
        max_tokens=2000,  # 增加输出长度以支持详细的图片分析和测试用例生成
        **kwargs
    )

# ============================================================================
# 模块级别的便捷访问
# ============================================================================

# 导出常用的类和函数
__all__ = [
    # 核心类
    "LLMFactory",
    "LLMConfig",
    "ModelType",
    
    # 便捷函数
    "create_llm",
    "create_chat_llm",
    "create_code_llm",
    "create_reasoning_llm",
    "create_fast_llm",
]

