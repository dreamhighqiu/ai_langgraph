"""
应用配置管理

使用 Pydantic Settings 管理应用配置，支持环境变量和 .env 文件
"""



from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 忽略额外的环境变量
    )
   
    enable_pdf_multimodal: bool = True  # 是否启用 PDF 多模态图片解析（需要配置 DOUBAO_API_KEY）

    # ========== LLM 配置 ==========
    # OpenAI 配置（主要使用）
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"  # 默认模型
    openai_base_url: Optional[str] = None  # 自定义 API 端点
    
    # DeepSeek 配置（备用）
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: Optional[str] = None  # 自定义 API 端点
    
    # Anthropic 配置（备用）
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # 默认 LLM 提供商（openai, deepseek, anthropic）
    default_llm_provider: str = "openai"

    # API 配置
    api_prefix: str = "/api/v2"  # API 路径前缀

    # 接口测试工作目录配置
    api_workspace_root: str = "agents/api/workspace"
    api_mcp_root: str = "mcp_servers/api"
    api_skills_root: str = "agents/api/agent_skills"

    # UI 测试工作目录配置 (TypeScript/Playwright)
    ui_workspace_root: str = "agents/ui/workspace"
    ui_mcp_root: str = "mcp_servers/ui"
    ui_skills_root: str = "agents/ui/agent_skills"

    # UI Java 测试工作目录配置 (Java/Playwright)
    ui_java_workspace_root: str = "agents/ui_java/workspace"
    ui_java_skills_root: str = "agents/ui_java/agent_skills"

    # 测试用例工作目录配置
    testcase_workspace_root: str = "agents/testcase/workspace"
    testcase_skills_root: str = "agents/testcase/agent_skills"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()


