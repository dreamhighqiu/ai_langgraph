"""
启动知识库处理器（后台任务）
"""
import asyncio
import sys
import os
import signal

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from module_testing.service.knowledge_processor import start_processor, stop_processor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_processor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("🚀 启动知识库处理器")
    logger.info("=" * 50)
    
    # 设置信号处理
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("收到停止信号，正在关闭...")
        asyncio.create_task(stop_processor())
        loop.stop()
    
    # 注册信号处理器（Windows 不支持 SIGTERM）
    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            loop.add_signal_handler(signal.SIGTERM, signal_handler)
    except NotImplementedError:
        # Windows 平台
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    
    try:
        # 启动处理器（每10秒检查一次）
        await start_processor(check_interval=10)
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"处理器运行异常: {e}", exc_info=True)
    finally:
        await stop_processor()
        logger.info("✅ 处理器已停止")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序已退出")


