from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    expected = settings.api_key
    if expected:
        if api_key == expected:
            return api_key
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    # 如果未配置 API Key，则允许匿名访问（开发模式）
    return ""
