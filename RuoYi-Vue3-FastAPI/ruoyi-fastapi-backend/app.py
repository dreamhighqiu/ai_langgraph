import uvicorn
import os

from config.env import AppConfig
from server import create_app

app = create_app()

if __name__ == '__main__':
    # 开发环境不使用 root_path，生产环境使用
    # 注意：h11实现不能处理None，必须使用空字符串
    app_env = os.getenv('APP_ENV', 'dev')
    root_path = '' if app_env == 'dev' else AppConfig.app_root_path
    
    # 如果启用reload，必须使用字符串路径；否则可以直接传递app对象
    if AppConfig.app_reload:
        # reload模式：使用字符串路径
        uvicorn.run(
            app='app:app',  # 字符串路径，支持reload
            host=AppConfig.app_host,
            port=AppConfig.app_port,
            root_path=root_path,
            reload=AppConfig.app_reload,
            log_level='info',
            access_log=True,
            loop='asyncio',  # 使用asyncio事件循环
            http='h11',  # 使用h11而不是httptools，更稳定
        )
    else:
        # 非reload模式：直接传递app对象，避免HTTP协议解析问题
        uvicorn.run(
            app=app,  # 直接传递app对象
            host=AppConfig.app_host,
            port=AppConfig.app_port,
            root_path=root_path,
            reload=False,
            log_level='info',
            access_log=True,
            loop='asyncio',  # 使用asyncio事件循环
            http='h11',  # 使用h11而不是httptools，更稳定
        )
