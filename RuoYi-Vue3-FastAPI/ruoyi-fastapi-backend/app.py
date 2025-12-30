import uvicorn
import os

from config.env import AppConfig
from server import create_app

app = create_app()

if __name__ == '__main__':
    # 开发环境不使用 root_path，生产环境使用
    app_env = os.getenv('APP_ENV', 'dev')
    root_path = None if app_env == 'dev' else AppConfig.app_root_path
    
    uvicorn.run(
        app='app:app',
        host=AppConfig.app_host,
        port=AppConfig.app_port,
        root_path=root_path,
        reload=AppConfig.app_reload,
    )
