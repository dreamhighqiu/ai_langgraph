from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from common.router import auto_register_routers
from config.env import AppConfig
from config.get_db import init_create_table
from config.get_redis import RedisUtil
from config.get_scheduler import SchedulerUtil
from exceptions.handle import handle_exception
from middlewares.handle import handle_middleware
from sub_applications.handle import handle_sub_applications
from utils.common_util import worship
from utils.log_util import logger


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f'⏰️ {AppConfig.app_name}开始启动')
    worship()
    await init_create_table()
    app.state.redis = await RedisUtil.create_redis_pool()
    await RedisUtil.init_sys_dict(app.state.redis)
    await RedisUtil.init_sys_config(app.state.redis)
    await SchedulerUtil.init_system_scheduler()
    
    # 配置 LightRAG 客户端
    try:
        import os
        from module_testing.service.lightrag_client import LightRAGManager
        
        lightrag_url = os.getenv('LIGHTRAG_BASE_URL', 'http://localhost:9621')
        lightrag_api_key = os.getenv('LIGHTRAG_API_KEY')
        LightRAGManager.configure(base_url=lightrag_url, api_key=lightrag_api_key)
        logger.info(f'✅ LightRAG 客户端配置成功: {lightrag_url}')
    except Exception as e:
        logger.warning(f'⚠️  LightRAG 客户端配置失败: {e}')
    
    # 启动知识库文件处理器（后台任务）
    try:
        import asyncio
        from module_testing.service.knowledge_processor import start_processor
        
        # 在后台任务中启动处理器
        async def start_knowledge_processor():
            try:
                await start_processor(check_interval=10)
                logger.info('✅ 知识库文件处理器启动成功')
            except Exception as e:
                logger.error(f'❌ 知识库文件处理器启动失败: {e}', exc_info=True)
        
        # 创建后台任务
        task = asyncio.create_task(start_knowledge_processor())
        app.state.knowledge_processor_task = task
    except Exception as e:
        logger.warning(f'⚠️  知识库文件处理器启动失败: {e}')
    
    logger.info(f'🚀 {AppConfig.app_name}启动成功')
    yield
    
    # 关闭知识库文件处理器
    try:
        from module_testing.service.knowledge_processor import stop_processor
        await stop_processor()
        logger.info('✅ 知识库文件处理器已停止')
    except Exception as e:
        logger.warning(f'⚠️  停止知识库文件处理器失败: {e}')
    
    await RedisUtil.close_redis_pool(app)
    await SchedulerUtil.close_system_scheduler()


def setup_docs_static_resources(
    redoc_js_url: str = 'https://registry.npmmirror.com/redoc/2/files/bundles/redoc.standalone.js',
    redoc_favicon_url: str = 'https://fastapi.tiangolo.com/img/favicon.png',
    swagger_js_url: str = 'https://registry.npmmirror.com/swagger-ui-dist/5/files/swagger-ui-bundle.js',
    swagger_css_url: str = 'https://registry.npmmirror.com/swagger-ui-dist/5/files/swagger-ui.css',
    swagger_favicon_url: str = 'https://fastapi.tiangolo.com/img/favicon.png',
) -> None:
    """
    配置文档静态资源

    :param redoc_js_url: 用于加载ReDoc JavaScript的URL
    :param redoc_favicon_url: ReDoc要使用的favicon的URL
    :param swagger_js_url: 用于加载Swagger UI JavaScript的URL
    :param swagger_css_url: 用于加载Swagger UI CSS的URL
    :param swagger_favicon_url: Swagger UI要使用的favicon的URL
    :return:
    """

    def redoc_monkey_patch(*args, **kwargs) -> HTMLResponse:
        return get_redoc_html(
            *args,
            **kwargs,
            redoc_js_url=redoc_js_url,
            redoc_favicon_url=redoc_favicon_url,
        )

    def swagger_ui_monkey_patch(*args, **kwargs) -> HTMLResponse:
        return get_swagger_ui_html(
            *args,
            **kwargs,
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
            swagger_favicon_url=swagger_favicon_url,
        )

    applications.get_redoc_html = redoc_monkey_patch
    applications.get_swagger_ui_html = swagger_ui_monkey_patch


def create_app() -> FastAPI:
    """
    创建FastAPI应用

    :return: FastAPI对象
    """
    # 配置文档静态资源
    setup_docs_static_resources()
    # 初始化FastAPI对象
    app = FastAPI(
        title=AppConfig.app_name,
        description=f'{AppConfig.app_name}接口文档',
        version=AppConfig.app_version,
        lifespan=lifespan,
    )

    # 挂载子应用
    handle_sub_applications(app)
    # 加载中间件处理方法
    handle_middleware(app)
    # 加载全局异常处理方法
    handle_exception(app)
    # 自动注册路由
    auto_register_routers(app)

    return app
