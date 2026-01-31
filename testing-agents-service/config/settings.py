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
    )
   
    enable_pdf_multimodal: bool = True  # 是否启用 PDF 多模态图片解析（需要配置 DOUBAO_API_KEY）

    # 大模型配置
    deepseek_api_key: Optional[str] = None


    # 接口测试工作目录配置
    api_workspace_root: str = "agents/api/workspace"
    api_mcp_root: str = "mcp/api"
    api_skills_root: str = "agents/api/agent_skills"

    # UI 测试工作目录配置
    ui_workspace_root: str = "agents/ui/workspace"
    ui_mcp_root: str = "mcp/ui"
    ui_skills_root: str = "agents/ui/agent_skills"

    # 测试用例工作目录配置
    testcase_workspace_root: str = "agents/testcase/workspace"
    testcase_skills_root: str = "agents/testcase/agent_skills"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()

