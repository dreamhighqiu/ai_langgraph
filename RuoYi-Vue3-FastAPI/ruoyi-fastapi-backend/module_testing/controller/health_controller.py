"""
健康检查接口：用于快速确认外部依赖联通性
"""
import socket
from typing import Annotated
from urllib.parse import urlparse

from fastapi import Request, Response

from common.router import APIRouterPro
from config.env import LangGraphConfig, MinIOConfig, MilvusConfig, RedisConfig
from config.get_redis import RedisUtil
from common.aspect.db_seesion import DBSessionDependency
from utils.response_util import ResponseUtil


health_controller = APIRouterPro(
    prefix="/testing/health",
    order_num=10,
    tags=["测试管理-健康检查"],
)


def _check_tcp(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _parse_host_port(url: str, default_port: int | None = None) -> tuple[str, int]:
    parsed = urlparse(url)
    if parsed.scheme:
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or default_port or (443 if parsed.scheme == "https" else 80)
        return host, port
    if ":" in url:
        host, port_str = url.split(":", 1)
        try:
            return host, int(port_str)
        except ValueError:
            return host, default_port or 80
    return url, default_port or 80


@health_controller.get("", summary="依赖健康检查")
async def health_check(
    request: Request,
    db=Annotated[object, DBSessionDependency()],
) -> Response:
    """
    检查关键外部依赖：数据库、Redis、MinIO、Milvus、LangGraph、Ollama/OpenAI
    """
    result: dict[str, dict] = {}

    # DB: 依赖注入能成功即为 OK
    result["database"] = {"ok": True}

    # Redis
    try:
        redis = request.app.state.redis if hasattr(request.app.state, "redis") else await RedisUtil.create_redis_pool()
        pong = await redis.ping()
        result["redis"] = {"ok": bool(pong)}
    except Exception as e:
        result["redis"] = {"ok": False, "error": str(e)}

    # MinIO
    minio_host, minio_port = _parse_host_port(MinIOConfig.minio_endpoint, 9000)
    result["minio"] = {"ok": _check_tcp(minio_host, minio_port)}

    # Milvus
    result["milvus"] = {"ok": _check_tcp(MilvusConfig.milvus_host, MilvusConfig.milvus_port)}

    # LangGraph
    lg_host, lg_port = _parse_host_port(LangGraphConfig.langgraph_api_url, 2025)
    result["langgraph"] = {"ok": _check_tcp(lg_host, lg_port)}

    # Ollama / OpenAI 兼容
    ollama_host, ollama_port = _parse_host_port(LangGraphConfig.langgraph_api_url, 11434)
    result["ollama"] = {"ok": _check_tcp(ollama_host, ollama_port)}

    # 汇总
    all_ok = all(item.get("ok") for item in result.values())
    status_msg = "healthy" if all_ok else "degraded"

    return ResponseUtil.success(
        msg=status_msg,
        data={"services": result, "all_ok": all_ok},
    )

