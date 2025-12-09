from fastapi import FastAPI

from .config import settings
from .database import init_db
from .routers import (
    agents,
    documents,
    mcp,
    rag,
    requirements,
    runs,
    sessions,
    testcases,
)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    api_prefix = settings.api_prefix
    app.include_router(agents.router, prefix=api_prefix)
    app.include_router(sessions.router, prefix=api_prefix)
    app.include_router(runs.router, prefix=api_prefix)
    app.include_router(requirements.router, prefix=api_prefix)
    app.include_router(testcases.router, prefix=api_prefix)
    app.include_router(documents.router, prefix=api_prefix)
    app.include_router(rag.router, prefix=api_prefix)
    app.include_router(mcp.router, prefix=api_prefix)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "platform_api.main:app",
        host="0.0.0.0",
        port=9100,
        reload=True,
        log_level=settings.log_level.lower(),
    )
