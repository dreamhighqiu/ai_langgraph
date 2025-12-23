#!/usr/bin/env python3
"""统一服务 API 启动脚本.

启动一个 FastAPI 服务，整合所有存储和数据服务的 API：
- 知识库管理 (整合 LightRAG)
- Milvus 向量数据库管理
- MinIO 对象存储管理
- 数据库操作

这个服务可以被多个前端调用：
- testing-deep-agents-ui
- autogen_study/web

默认端口: 8080
"""

import os
import sys
import logging
from pathlib import Path

# 添加 src 到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def create_app():
    """创建 FastAPI 应用."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from unified_services.api import router
    
    app = FastAPI(
        title="统一服务 API",
        description="""
整合的存储和数据服务 API，提供：

- **知识库管理** - 整合 LightRAG，支持文档上传、语义搜索、问答
- **Milvus 管理** - 向量数据库操作，支持 Collection 管理和向量搜索
- **MinIO 管理** - 对象存储操作，支持 Bucket 和文件管理
- **健康检查** - 检查所有服务的运行状态

可以被多个前端应用共享调用。
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(router)
    
    # 健康检查
    @app.get("/ok")
    async def health():
        return {"status": "ok", "service": "unified-services-api"}
    
    @app.get("/")
    async def root():
        return {
            "service": "Unified Services API",
            "version": "1.0.0",
            "docs": "/docs",
            "endpoints": {
                "knowledge": "/api/v1/services/knowledge",
                "milvus": "/api/v1/services/milvus",
                "minio": "/api/v1/services/minio",
                "health": "/api/v1/services/health",
            }
        }
    
    return app


def main():
    """启动服务."""
    import uvicorn
    
    # 加载环境变量
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print("✅ Loaded environment from .env")
    except ImportError:
        pass
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    port = int(os.getenv("UNIFIED_API_PORT", "8080"))
    host = os.getenv("UNIFIED_API_HOST", "0.0.0.0")
    
    print("🚀 Starting Unified Services API...")
    print("\n" + "=" * 60)
    print(f"📍 Server URL: http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print(f"💚 Health Check: http://localhost:{port}/ok")
    print("\n📌 API Endpoints:")
    print(f"   • 知识库: http://localhost:{port}/api/v1/services/knowledge")
    print(f"   • Milvus: http://localhost:{port}/api/v1/services/milvus")
    print(f"   • MinIO:  http://localhost:{port}/api/v1/services/minio")
    print(f"   • 健康检查: http://localhost:{port}/api/v1/services/health")
    print("=" * 60 + "\n")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()

