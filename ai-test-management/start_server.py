#!/usr/bin/env python3
"""
Simple LangGraph API Server

A minimal script to start the LangGraph API server directly using uvicorn.
"""



import os
import sys
import json
from pathlib import Path
# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oWlV3PT06NzU3ODk3NWE=

def setup_environment():
    """Setup required environment variables"""
    project_root = Path(__file__).parent

    # Ensure backend package imports work (backend/app => import app.*)
    backend_path = project_root / "backend"
    if backend_path.exists():
        sys.path.insert(0, str(backend_path))
    
    # Load graphs from graph.json
    config_path = project_root / "graph.json"
    graphs = {}
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            graphs = config.get("graphs", {})
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oWlV3PT06NzU3ODk3NWE=
    
    host = os.getenv("LANGGRAPH_HOST", "0.0.0.0")
    port = int(os.getenv("LANGGRAPH_PORT", "2026"))
    api_url = os.getenv("LANGGRAPH_API_URL", f"http://localhost:{port}")

    # Set environment variables
    os.environ.update({
        # Database and storage - 使用自定义 PostgreSQL checkpointer
        # "POSTGRES_URI": "postgresql://postgres:postgres@localhost:5432/langgraph_checkpointer_db?sslmode=disable",
        # "REDIS_URI": "redis://localhost:6379",
        "DATABASE_URI": ":memory:",
        "REDIS_URI": "fake",
        # "MIGRATIONS_PATH": "/storage/migrations",
        "MIGRATIONS_PATH": "__inmem",
        # Server configuration
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_UI_BUNDLER": "true",
        "LANGGRAPH_RUNTIME_EDITION": "inmem",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_API_URL": api_url,

        # "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "1000",
        
        # Graphs configuration
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
        
        # Worker configuration
        "N_JOBS_PER_WORKER": "1",
    })
    
    # Load .env file if exists
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ Loaded environment from .env")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env file")

    return host, port

def main():
    """Start the server"""
    print("🚀 Starting Simple LangGraph API Server...")
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oWlV3PT06NzU3ODk3NWE=
    
    # Setup environment
    host, port = setup_environment()
    
    # Print server information
    print("\n" + "="*60)
    print(f"📍 Server URL: http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print(f"🎨 Studio UI: http://localhost:{port}/ui")
    print(f"💚 Health Check: http://localhost:{port}/ok")
    print("="*60)
    
    try:
        # Import uvicorn after environment setup
        import uvicorn
        
        reload = os.getenv("LANGGRAPH_RELOAD", "true").lower() in {"1", "true", "yes", "y"}

        # Start the server directly
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
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oWlV3PT06NzU3ODk3NWE=
