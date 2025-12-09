import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    load_dotenv()


class Settings(BaseModel):
    app_name: str = Field(default="AI Productivity Platform API")
    api_prefix: str = Field(default="/api")
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "PLATFORM_DATABASE_URL",
            "mysql+pymysql://root:root@localhost:3306/platform_db",
        )
    )
    log_level: str = Field(default_factory=lambda: os.getenv("PLATFORM_LOG_LEVEL", "INFO"))
    api_key: str | None = Field(default_factory=lambda: os.getenv("PLATFORM_API_KEY"))
    lightrag_base_url: str = Field(
        default_factory=lambda: os.getenv("LIGHTRAG_BASE_URL", "http://localhost:9621")
    )
    mcp_base_url: str = Field(
        default_factory=lambda: os.getenv("MCP_BASE_URL", "http://localhost:8001")
    )
    minio_endpoint: str = Field(default_factory=lambda: os.getenv("MINIO_ENDPOINT", "localhost:9000"))
    minio_access_key: str = Field(default_factory=lambda: os.getenv("MINIO_ACCESS_KEY", "minioadmin"))
    minio_secret_key: str = Field(default_factory=lambda: os.getenv("MINIO_SECRET_KEY", "minioadmin"))
    minio_bucket: str = Field(default_factory=lambda: os.getenv("MINIO_BUCKET", "original-requirements"))
    minio_secure: bool = Field(default_factory=lambda: os.getenv("MINIO_SECURE", "false").lower() == "true")
    minio_public_url: str = Field(default_factory=lambda: os.getenv("MINIO_PUBLIC_URL", ""))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
