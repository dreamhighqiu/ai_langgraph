#!/usr/bin/env python3
"""
LangGraph API Server 启动脚本

参照 ai-test-management 项目实现
提供 LangGraph 智能体服务，供前端 LangGraph SDK 调用
"""

import os
import sys
import json
import io
from pathlib import Path

# 避免 Windows 控制台编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def setup_environment():
    """设置必要的环境变量"""
    project_root = Path(__file__).parent
    
    # 确保项目根目录在 Python 路径中
    sys.path.insert(0, str(project_root))
    
    # 加载 graphs 配置
    config_path = project_root / "module_testing" / "agents" / "graph.json"
    graphs = {}
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            graphs = config.get("graphs", {})
            print(f"✅ 加载了 {len(graphs)} 个 Agent 配置")
            for name in graphs.keys():
                print(f"   - {name}")
    else:
        print("⚠️ 未找到 graph.json 配置文件")
    
    # 从环境变量读取配置
    host = os.getenv("LANGGRAPH_HOST", "0.0.0.0")
    port = int(os.getenv("LANGGRAPH_PORT", "2025"))
    api_url = os.getenv("LANGGRAPH_API_URL", f"http://localhost:{port}")
    
    # 设置 LangGraph 环境变量
    os.environ.update({
        # 数据库和存储配置 - 使用内存模式
        "DATABASE_URI": ":memory:",
        "REDIS_URI": "fake",
        "MIGRATIONS_PATH": "__inmem",
        
        # 服务器配置
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_UI_BUNDLER": "true",
        "LANGGRAPH_RUNTIME_EDITION": "inmem",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_API_URL": api_url,
        
        # Graphs 配置
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
        
        # Worker 配置
        "N_JOBS_PER_WORKER": "1",
    })
    
    # 加载 .env 文件
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ 从 .env 加载环境变量")
        except ImportError:
            print("⚠️ python-dotenv 未安装，跳过 .env 加载")
    
    return host, port


def main():
    """启动服务"""
    print("🚀 启动 LangGraph API 服务...")
    print("=" * 60)
    
    # 设置环境
    host, port = setup_environment()
    
    # 打印服务信息
    print(f"\n📍 服务地址: http://localhost:{port}")
    print(f"📚 API 文档: http://localhost:{port}/docs")
    print(f"🎨 Studio UI: http://localhost:{port}/ui")
    print(f"💚 健康检查: http://localhost:{port}/ok")
    print("=" * 60)
    
    try:
        import uvicorn
        
        reload = os.getenv("LANGGRAPH_RELOAD", "true").lower() in {"1", "true", "yes", "y"}
        
        # 启动服务
        uvicorn.run(
            "langgraph_api.server:app",
            host=host,
            port=port,
            reload=reload,
            access_log=False,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    }
                },
                "handlers": {
                    "default": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    }
                },
                "root": {
                    "level": "INFO",
                    "handlers": ["default"],
                },
                "loggers": {
                    "uvicorn": {"level": "INFO"},
                    "uvicorn.error": {"level": "INFO"},
                    "uvicorn.access": {"level": "WARNING"},
                }
            }
        )
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install langgraph-api uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

