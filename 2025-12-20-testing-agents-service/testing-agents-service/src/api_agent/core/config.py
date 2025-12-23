"""
API Agent配置模块

提供配置管理、环境变量加载和配置验证功能。
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from functools import lru_cache


# ============================================================================
# 目录配置
# ============================================================================

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
# API Agent目录
API_AGENT_DIR = Path(__file__).parent.parent
# 默认输出目录
DEFAULT_OUTPUT_DIR = API_AGENT_DIR / "api-test-outputs"


# ============================================================================
# 配置模型
# ============================================================================
# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVVWU1VBPT06YmRjZTJhMDI=

class LLMConfig(BaseModel):
    """LLM配置"""
    model_name: str = Field(
        default="deepseek-chat",
        description="LLM模型名称"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API密钥，优先从环境变量读取"
    )
    api_base: str = Field(
        default="https://api.deepseek.com/v1",
        description="API基础URL"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度"
    )
    max_tokens: int = Field(
        default=4096,
        gt=0,
        description="最大token数"
    )
    
    @field_validator("api_key", mode="before")
    @classmethod
    def get_api_key(cls, v):
        """从环境变量获取API密钥"""
        if v is None:
            v = os.getenv("DEEPSEEK_API_KEY", "sk-868325fd211f4303a106658a98bb9aab") or os.getenv("OPENAI_API_KEY")
        return v


class MCPServerConfig(BaseModel):
    """MCP服务器配置"""
    pytest_generator_host: str = Field(
        default="localhost",
        description="Pytest生成器主机"
    )
    pytest_generator_port: int = Field(
        default=8003,
        ge=1,
        le=65535,
        description="Pytest生成器端口"
    )
    test_executor_host: str = Field(
        default="localhost",
        description="测试执行器主机"
    )
    test_executor_port: int = Field(
        default=8004,
        ge=1,
        le=65535,
        description="测试执行器端口"
    )
    rag_server_host: str = Field(
        default="localhost",
        description="RAG服务器主机"
    )
    rag_server_port: int = Field(
        default=8002,
        ge=1,
        le=65535,
        description="RAG服务器端口"
    )
    connection_timeout: float = Field(
        default=30.0,
        gt=0,
        description="连接超时时间（秒）"
    )
    
    @property
    def pytest_generator_url(self) -> str:
        """获取pytest生成器SSE URL"""
        return f"http://{self.pytest_generator_host}:{self.pytest_generator_port}/sse"
    
    @property
    def test_executor_url(self) -> str:
        """获取测试执行器SSE URL"""
        return f"http://{self.test_executor_host}:{self.test_executor_port}/sse"
    
    @property
    def rag_server_url(self) -> str:
        """获取RAG服务器SSE URL"""
        return f"http://{self.rag_server_host}:{self.rag_server_port}/sse"
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVVWU1VBPT06YmRjZTJhMDI=


class TestExecutionConfig(BaseModel):
    """测试执行配置"""
    output_dir: str = Field(
        default=str(DEFAULT_OUTPUT_DIR),
        description="测试输出目录"
    )
    parallel_workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="并行执行的工作进程数"
    )
    default_timeout: int = Field(
        default=300,
        gt=0,
        description="默认测试超时时间（秒）"
    )
    enable_allure: bool = Field(
        default=True,
        description="是否启用Allure报告"
    )
    allure_results_dir: str = Field(
        default="./allure-results",
        description="Allure原始结果目录（JSON格式）"
    )
    allure_report_dir: str = Field(
        default="./allure-report",
        description="Allure HTML报告目录"
    )
    verbose: bool = Field(
        default=True,
        description="是否启用详细输出"
    )
    fail_fast: bool = Field(
        default=False,
        description="遇到失败时是否立即停止"
    )
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVVWU1VBPT06YmRjZTJhMDI=


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="日志级别"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="日志文件路径"
    )
    console_output: bool = Field(
        default=True,
        description="是否输出到控制台"
    )


class AgentConfig(BaseModel):
    """Agent完整配置"""
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM配置"
    )
    mcp_servers: MCPServerConfig = Field(
        default_factory=MCPServerConfig,
        description="MCP服务器配置"
    )
    test_execution: TestExecutionConfig = Field(
        default_factory=TestExecutionConfig,
        description="测试执行配置"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="日志配置"
    )
    
    # 便捷属性
    @property
    def model_name(self) -> str:
        return self.llm.model_name
    
    @property
    def api_key(self) -> Optional[str]:
        return self.llm.api_key
    
    @property
    def output_dir(self) -> str:
        return self.test_execution.output_dir
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """从环境变量创建配置"""
        return cls(
            llm=LLMConfig(
                model_name=os.getenv("LLM_MODEL_NAME", "deepseek-chat"),
                api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
                api_base=os.getenv("LLM_API_BASE", "https://api.deepseek.com/v1"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096"))
            ),
            mcp_servers=MCPServerConfig(
                pytest_generator_port=int(os.getenv("PYTEST_GENERATOR_PORT", "8003")),
                test_executor_port=int(os.getenv("TEST_EXECUTOR_PORT", "8004")),
                rag_server_port=int(os.getenv("RAG_SERVER_PORT", "8002"))
            ),
            test_execution=TestExecutionConfig(
                output_dir=os.getenv("TEST_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)),
                parallel_workers=int(os.getenv("PARALLEL_WORKERS", "4")),
                default_timeout=int(os.getenv("TEST_TIMEOUT", "300")),
                allure_results_dir=os.getenv("ALLURE_RESULTS_DIR", "./allure-results"),
                allure_report_dir=os.getenv("ALLURE_REPORT_DIR", "./allure-report")
            ),
            logging=LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO")
            )
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()


# ============================================================================
# 全局配置获取
# ============================================================================
# type: ignore  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVVWU1VBPT06YmRjZTJhMDI=

@lru_cache(maxsize=1)
def get_config() -> AgentConfig:
    """获取全局配置（单例模式）"""
    return AgentConfig.from_env()


def reset_config():
    """重置配置缓存"""
    get_config.cache_clear()

