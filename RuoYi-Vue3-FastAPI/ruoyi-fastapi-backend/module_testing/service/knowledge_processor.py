"""
知识库文件处理器（后台任务）
监听 pending 状态的文件，异步处理并上传到 LightRAG
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from module_testing.dao.knowledge_dao import KnowledgeDao, KnowledgeFileDao
from module_testing.entity.do.knowledge_do import TestKnowledgeFile
from module_testing.storage.minio_client import MinioClientManager
from module_testing.service.lightrag_client import get_lightrag_manager
from config.env import DataBaseConfig

logger = logging.getLogger(__name__)


class KnowledgeProcessor:
    """知识库文件处理器"""
    
    def __init__(self, check_interval: int = 10):
        """
        初始化处理器
        
        Args:
            check_interval: 检查间隔（秒）
        """
        self.check_interval = check_interval
        self.running = False
        
        # 创建独立的数据库引擎
        self.engine = create_async_engine(
            DataBaseConfig.db_url,
            echo=DataBaseConfig.db_echo,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.async_session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(f'知识库处理器初始化完成，检查间隔: {check_interval}秒')
    
    async def start(self):
        """启动处理器"""
        if self.running:
            logger.warning('处理器已在运行中')
            return
        
        self.running = True
        logger.info('知识库处理器启动')
        
        while self.running:
            try:
                await self._process_pending_files()
            except Exception as e:
                logger.error(f'处理文件时发生错误: {e}', exc_info=True)
            
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """停止处理器"""
        self.running = False
        await self.engine.dispose()
        logger.info('知识库处理器停止')
    
    async def _process_pending_files(self):
        """处理待处理的文件"""
        async with self.async_session_factory() as db:
            try:
                # 查询 pending 状态的文件
                query = select(TestKnowledgeFile).where(
                    TestKnowledgeFile.process_status == 'pending'
                ).limit(5)  # 每次最多处理5个文件
                
                result = await db.execute(query)
                pending_files = result.scalars().all()
                
                if not pending_files:
                    return
                
                logger.info(f'发现 {len(pending_files)} 个待处理文件')
                
                # 并发处理文件
                tasks = [
                    self._process_single_file(db, file)
                    for file in pending_files
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception as e:
                logger.error(f'查询待处理文件失败: {e}', exc_info=True)
    
    async def _process_single_file(self, db: AsyncSession, file: TestKnowledgeFile):
        """
        处理单个文件
        
        Args:
            db: 数据库会话
            file: 文件记录
        """
        file_id = file.file_id
        
        try:
            logger.info(f'开始处理文件: {file.file_name} (file_id: {file_id})')
            
            # 1. 更新状态为 processing
            await KnowledgeFileDao.update_file_status(db, file_id, 'processing', 10)
            await db.commit()
            
            # 2. 获取知识库信息
            knowledge = await KnowledgeDao.select_knowledge_by_id(db, file.knowledge_id)
            if not knowledge:
                raise Exception('知识库不存在')
            
            logger.debug(f'知识库信息: {knowledge.knowledge_name} (Collection: {knowledge.milvus_collection_name})')
            
            # 3. 从 MinIO 下载文件
            logger.debug(f'从 MinIO 下载文件: {file.file_path}')
            minio_client = MinioClientManager.get_client()
            file_content = await minio_client.download_file_async(file.file_path)
            
            await KnowledgeFileDao.update_file_status(db, file_id, 'processing', 30)
            await db.commit()
            
            # 4. 上传到 LightRAG
            logger.debug(f'上传到 LightRAG: {file.file_name}')
            lightrag_manager = get_lightrag_manager()
            
            upload_result = await lightrag_manager.upload_document(
                collection_name=knowledge.milvus_collection_name,
                file_content=file_content,
                filename=file.file_name,
                metadata={
                    'file_id': file_id,
                    'knowledge_id': file.knowledge_id,
                    'file_name': file.file_name,
                    'file_path': file.file_path
                }
            )
            
            logger.debug(f'LightRAG 上传结果: {upload_result}')
            
            # 5. 更新状态为 completed
            doc_id = upload_result.get('doc_id') or upload_result.get('track_id')
            await KnowledgeFileDao.update_file_status(db, file_id, 'processing', 80)
            await db.commit()
            
            # 更新文件记录
            await db.execute(
                TestKnowledgeFile.__table__.update()
                .where(TestKnowledgeFile.file_id == file_id)
                .values(
                    doc_id=doc_id,
                    process_status='completed',
                    process_progress=100,
                    process_end_time=datetime.now()
                )
            )
            await db.commit()
            
            # 6. 更新知识库统计
            stats = await KnowledgeFileDao.get_knowledge_stats(db, file.knowledge_id)
            await KnowledgeDao.update_knowledge_stats(
                db,
                file.knowledge_id,
                stats['file_count'],
                stats['vector_count']
            )
            await db.commit()
            
            logger.info(f'文件处理成功: {file.file_name} (file_id: {file_id}, doc_id: {doc_id})')
            
        except Exception as e:
            logger.error(f'文件处理失败: {file.file_name} (file_id: {file_id}), 错误: {e}', exc_info=True)
            
            # 更新状态为 failed
            try:
                await KnowledgeFileDao.update_file_status(
                    db,
                    file_id,
                    'failed',
                    error_msg=str(e)
                )
                await db.commit()
            except Exception as update_error:
                logger.error(f'更新失败状态时出错: {update_error}')


# 全局处理器实例
_processor: Optional[KnowledgeProcessor] = None


async def start_processor(check_interval: int = 10):
    """启动处理器"""
    global _processor
    
    if _processor is not None:
        logger.warning('处理器已存在')
        return
    
    _processor = KnowledgeProcessor(check_interval)
    await _processor.start()


async def stop_processor():
    """停止处理器"""
    global _processor
    
    if _processor is None:
        logger.warning('处理器未启动')
        return
    
    await _processor.stop()
    _processor = None


def get_processor() -> Optional[KnowledgeProcessor]:
    """获取处理器实例"""
    return _processor


