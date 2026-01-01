"""
知识库服务层
"""
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.knowledge_dao import KnowledgeDao, KnowledgeFileDao
from module_testing.entity.do.knowledge_do import TestKnowledge, TestKnowledgeFile
from module_testing.entity.vo.knowledge_vo import (
    KnowledgeModel,
    KnowledgeCreateModel,
    KnowledgeUpdateModel,
    KnowledgeQueryModel,
    KnowledgeStatsModel,
    KnowledgeFileModel,
    KnowledgeFileQueryModel,
)
from module_testing.storage.minio_client import MinioClientManager
from module_testing.service.lightrag_client import get_lightrag_manager

logger = logging.getLogger(__name__)


class KnowledgeService:
    """知识库服务"""
    
    @staticmethod
    def _generate_workspace_name(project_id: int) -> str:
        """
        生成 Milvus Collection 名称（作为 LightRAG workspace）
        简化逻辑：直接使用项目ID，确保项目与workspace一对一
        
        Args:
            project_id: 项目ID
        
        Returns:
            Workspace 名称（例如: project_1）
        """
        return f'project_{project_id}'
    
    @staticmethod
    async def get_or_create_knowledge_by_project(
        db: AsyncSession,
        project_id: int,
        project_name: Optional[str] = None,
        create_by: Optional[str] = None
    ) -> TestKnowledge:
        """
        获取或创建项目的知识库（项目与知识库一对一）
        
        如果项目有多个知识库，会保留最新的一个，其他的会被标记为待清理。
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            project_name: 项目名称（用于创建知识库时的默认名称）
            create_by: 创建者
        
        Returns:
            知识库对象
        """
        # 先尝试根据项目ID查找知识库
        knowledge = await KnowledgeDao.select_knowledge_by_project_id(db, project_id)
        
        if knowledge:
            # 检查是否有多个知识库（数据不一致的情况）
            all_knowledges = await KnowledgeDao.select_knowledge_list_by_project_id(db, project_id)
            if len(all_knowledges) > 1:
                logger.warning(f'项目 {project_id} 存在多个知识库（{len(all_knowledges)}个），将使用最新的一个（ID: {knowledge.knowledge_id}）')
                # 可以在这里添加清理逻辑，删除旧的知识库
                # 但为了安全，暂时只记录警告，不自动删除
            return knowledge
        
        # 如果不存在，自动创建
        workspace_name = KnowledgeService._generate_workspace_name(project_id)
        knowledge_name = project_name or f'项目{project_id}知识库'
        
        knowledge = TestKnowledge(
            project_id=project_id,
            knowledge_name=knowledge_name,
            description=f'{knowledge_name} - 自动创建',
            collection_name=workspace_name,
            file_count=0,
            vector_count=0,
            status='0',
            create_by=create_by or 'system',
            create_time=datetime.now()
        )
        
        created = await KnowledgeDao.insert_knowledge(db, knowledge)
        await db.commit()
        await db.refresh(created)
        
        logger.info(f'自动创建项目知识库: project_id={project_id}, workspace={workspace_name}')
        
        # 初始化 Milvus 集合（通过上传占位文档触发集合创建）
        try:
            lightrag_manager = get_lightrag_manager()
            await lightrag_manager.init_workspace(workspace_name)
            logger.info(f'Milvus 集合初始化成功: {workspace_name}')
        except Exception as e:
            logger.warning(f'Milvus 集合初始化失败: {workspace_name}, 错误: {e}。集合将在首次上传文档时自动创建。')
        
        return created
    
    @staticmethod
    async def create_knowledge(
        db: AsyncSession,
        knowledge_create: KnowledgeCreateModel,
        create_by: str
    ) -> KnowledgeModel:
        """
        创建知识库
        
        Args:
            db: 数据库会话
            knowledge_create: 创建参数
            create_by: 创建者
        
        Returns:
            知识库模型
        """
        # 创建知识库记录（暂时不设置 collection_name）
        knowledge = TestKnowledge(
            project_id=knowledge_create.project_id,
            knowledge_name=knowledge_create.knowledge_name,
            description=knowledge_create.description,
            collection_name='',  # 临时值
            file_count=0,
            vector_count=0,
            status='0',
            create_by=create_by,
            create_time=datetime.now(),
            remark=knowledge_create.remark
        )
        
        # 检查项目是否已有知识库（项目与知识库一对一）
        existing_list = await KnowledgeDao.select_knowledge_list_by_project_id(db, knowledge_create.project_id)
        if existing_list:
            # 如果存在多个，使用最新的一个
            existing = existing_list[0] if existing_list else None
            if existing:
                if len(existing_list) > 1:
                    logger.warning(f'项目 {knowledge_create.project_id} 存在多个知识库，将保留最新的（ID: {existing.knowledge_id}）')
                raise ValueError(f'项目 {knowledge_create.project_id} 已存在知识库（ID: {existing.knowledge_id}），一个项目只能有一个知识库')
        
        # 生成 Workspace 名称（直接使用项目ID）
        workspace_name = KnowledgeService._generate_workspace_name(knowledge_create.project_id)
        
        # 设置 collection_name
        knowledge.collection_name = workspace_name
        
        # 插入数据库
        created = await KnowledgeDao.insert_knowledge(db, knowledge)
        await db.commit()
        await db.refresh(created)
        
        logger.info(f'知识库创建成功: {created.knowledge_id}, Workspace: {workspace_name}')
        
        # 初始化 Milvus 集合（通过上传占位文档触发集合创建）
        try:
            lightrag_manager = get_lightrag_manager()
            await lightrag_manager.init_workspace(workspace_name)
            logger.info(f'Milvus 集合初始化成功: {workspace_name}')
        except Exception as e:
            # 如果初始化失败，记录警告但不影响知识库创建
            logger.warning(f'Milvus 集合初始化失败: {workspace_name}, 错误: {e}。集合将在首次上传文档时自动创建。')
        
        return KnowledgeModel.model_validate(created)
    
    @staticmethod
    async def get_knowledge_by_id(db: AsyncSession, knowledge_id: int) -> Optional[KnowledgeModel]:
        """根据ID获取知识库"""
        knowledge = await KnowledgeDao.select_knowledge_by_id(db, knowledge_id)
        if knowledge:
            return KnowledgeModel.model_validate(knowledge)
        return None
    
    @staticmethod
    async def get_knowledge_list(
        db: AsyncSession,
        query: KnowledgeQueryModel
    ) -> Tuple[List[KnowledgeModel], int]:
        """获取知识库列表"""
        knowledge_list, total = await KnowledgeDao.select_knowledge_list(db, query)
        return [KnowledgeModel.model_validate(k) for k in knowledge_list], total
    
    @staticmethod
    async def update_knowledge(
        db: AsyncSession,
        knowledge_update: KnowledgeUpdateModel,
        update_by: str
    ) -> bool:
        """
        更新知识库
        
        注意：如果知识库名称改变，会重新生成 workspace 名称。
        旧的 workspace 数据会保留，新上传的文件会使用新的 workspace。
        """
        # 获取当前知识库信息
        knowledge = await KnowledgeDao.select_knowledge_by_id(db, knowledge_update.knowledge_id)
        if not knowledge:
            return False
        
        update_data = {
            'update_by': update_by,
            'update_time': datetime.now()
        }
        
        # 注意：workspace 名称基于项目ID，不会因为知识库名称改变而改变
        # workspace 格式：project_{project_id}，确保项目与知识库一对一
        if knowledge_update.knowledge_name and knowledge_update.knowledge_name != knowledge.knowledge_name:
            update_data['knowledge_name'] = knowledge_update.knowledge_name
            # workspace 保持不变（基于项目ID）
            logger.info(f'知识库名称改变: {knowledge.knowledge_name} -> {knowledge_update.knowledge_name}，workspace 保持不变: {knowledge.collection_name}')
        elif knowledge_update.knowledge_name:
            update_data['knowledge_name'] = knowledge_update.knowledge_name
        
        if knowledge_update.description is not None:
            update_data['description'] = knowledge_update.description
        if knowledge_update.status:
            update_data['status'] = knowledge_update.status
        if knowledge_update.remark is not None:
            update_data['remark'] = knowledge_update.remark
        
        success = await KnowledgeDao.update_knowledge_by_id(
            db,
            knowledge_update.knowledge_id,
            **update_data
        )
        if success:
            await db.commit()
        
        return success
    
    @staticmethod
    async def delete_knowledge(db: AsyncSession, knowledge_id: int, delete_by: str) -> bool:
        """
        删除知识库
        
        Args:
            db: 数据库会话
            knowledge_id: 知识库ID
            delete_by: 删除者
        
        Returns:
            是否成功
        """
        # 获取知识库信息
        knowledge = await KnowledgeDao.select_knowledge_by_id(db, knowledge_id)
        if not knowledge:
            return False
        
        # 删除 LightRAG workspace（清空所有文档和向量）
        try:
            lightrag_manager = get_lightrag_manager()
            await lightrag_manager.delete_workspace(knowledge.collection_name)
            logger.info(f'LightRAG workspace 删除成功: {knowledge.collection_name}')
        except Exception as e:
            logger.warning(f'LightRAG workspace 删除失败: {e}')
        
        # 删除 MinIO 中的文件
        try:
            files = await db.execute(
                KnowledgeFileDao.select_file_list(
                    db,
                    KnowledgeFileQueryModel(
                        page_num=1,
                        page_size=1000,
                        knowledge_id=knowledge_id
                    )
                )
            )
            minio_client = MinioClientManager.get_client()
            for file in files[0]:
                try:
                    minio_client.delete_file(file.file_path)
                except Exception as e:
                    logger.warning(f'MinIO 文件删除失败: {file.file_path}, 错误: {e}')
        except Exception as e:
            logger.warning(f'MinIO 文件批量删除失败: {e}')
        
        # 删除数据库中的文件记录
        await KnowledgeFileDao.delete_files_by_knowledge_id(db, knowledge_id)
        
        # 删除知识库
        success = await KnowledgeDao.delete_knowledge_by_id(db, knowledge_id)
        if success:
            await db.commit()
            logger.info(f'知识库删除成功: {knowledge_id}')
        
        return success
    
    @staticmethod
    async def delete_knowledges(db: AsyncSession, knowledge_ids: List[int], delete_by: str) -> int:
        """
        批量删除知识库
        
        Args:
            db: 数据库会话
            knowledge_ids: 知识库ID列表
            delete_by: 删除者
        
        Returns:
            成功删除的数量
        """
        if not knowledge_ids:
            return 0
        
        success_count = 0
        for knowledge_id in knowledge_ids:
            try:
                success = await KnowledgeService.delete_knowledge(db, knowledge_id, delete_by)
                if success:
                    success_count += 1
            except Exception as e:
                logger.error(f'删除知识库失败 {knowledge_id}: {e}', exc_info=True)
        
        return success_count
    
    @staticmethod
    async def get_knowledge_stats(db: AsyncSession, knowledge_id: int) -> KnowledgeStatsModel:
        """获取知识库统计信息"""
        stats = await KnowledgeFileDao.get_knowledge_stats(db, knowledge_id)
        return KnowledgeStatsModel(**stats)
    
    @staticmethod
    async def upload_knowledge_file_by_project(
        db: AsyncSession,
        project_id: int,
        file: UploadFile,
        create_by: str,
        remark: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        通过项目ID上传文件到知识库（项目与知识库一对一）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            file: 上传的文件
            create_by: 创建者
            remark: 备注
        
        Returns:
            上传结果
        """
        # 获取项目信息（用于自动创建知识库）
        from module_testing.dao.project_dao import ProjectDAO
        project = await ProjectDAO.get_by_id(db, project_id)
        if not project:
            raise ValueError('项目不存在')
        
        # 获取或创建项目的知识库（项目与知识库一对一）
        knowledge = await KnowledgeService.get_or_create_knowledge_by_project(
            db=db,
            project_id=project_id,
            project_name=project.project_name,
            create_by=create_by
        )
        
        # 继续使用原有的上传逻辑
        return await KnowledgeService.upload_knowledge_file(
            db=db,
            knowledge_id=knowledge.knowledge_id,
            file=file,
            create_by=create_by,
            remark=remark
        )
    
    @staticmethod
    async def upload_knowledge_file(
        db: AsyncSession,
        knowledge_id: int,
        file: UploadFile,
        create_by: str,
        remark: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传知识库文件
        
        Args:
            db: 数据库会话
            knowledge_id: 知识库ID
            file: 上传的文件
            create_by: 创建者
            remark: 备注
        
        Returns:
            上传结果
        """
        # 验证知识库是否存在
        knowledge = await KnowledgeDao.select_knowledge_by_id(db, knowledge_id)
        if not knowledge:
            raise ValueError('知识库不存在')
        
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 上传到 MinIO
        minio_client = MinioClientManager.get_client()
        object_name = f'knowledge/{knowledge_id}/{datetime.now().strftime("%Y%m%d")}/{file.filename}'
        
        # MinIOClient.upload_file 方法签名: upload_file(file_content: bytes, object_name: str, content_type: str)
        # 返回: (success: bool, file_path: str) - file_path 包含完整路径（minio://bucket/path 或 local://bucket/path）
        success, file_path = minio_client.upload_file(
            file_content=content,
            object_name=object_name,
            content_type=file.content_type or 'application/octet-stream'
        )
        
        if not success:
            raise Exception(f'文件上传失败: {file_path}')
        
        # 创建文件记录
        file_record = TestKnowledgeFile(
            knowledge_id=knowledge_id,
            file_name=file.filename,
            file_path=file_path,  # 使用返回的完整路径
            file_size=file_size,
            process_status='pending',
            process_progress=0,
            vector_count=0,
            create_by=create_by,
            create_time=datetime.now()
        )
        
        created_file = await KnowledgeFileDao.insert_file(db, file_record)
        await db.commit()
        await db.refresh(created_file)
        
        logger.info(f'文件上传成功: {file.filename} (file_id: {created_file.file_id})')
        
        # 返回结果（实际处理由 KnowledgeProcessor 异步完成）
        return {
            'file_id': created_file.file_id,
            'file_name': created_file.file_name,
            'file_size': created_file.file_size,
            'status': created_file.process_status,
            'message': '文件已上传，正在处理中...'
        }
    
    @staticmethod
    async def get_file_list(
        db: AsyncSession,
        query: KnowledgeFileQueryModel
    ) -> Tuple[List[KnowledgeFileModel], int]:
        """获取文件列表"""
        file_list, total = await KnowledgeFileDao.select_file_list(db, query)
        return [KnowledgeFileModel.model_validate(f) for f in file_list], total
    
    @staticmethod
    async def get_file_by_id(db: AsyncSession, file_id: int) -> Optional[KnowledgeFileModel]:
        """根据ID获取文件"""
        file = await KnowledgeFileDao.select_file_by_id(db, file_id)
        if file:
            return KnowledgeFileModel.model_validate(file)
        return None
    
    @staticmethod
    async def delete_file(db: AsyncSession, file_id: int, delete_by: str) -> bool:
        """删除文件"""
        file = await KnowledgeFileDao.select_file_by_id(db, file_id)
        if not file:
            return False
        
        # 删除 LightRAG 中的文档
        if file.doc_id:
            try:
                knowledge = await KnowledgeDao.select_knowledge_by_id(db, file.knowledge_id)
                lightrag_manager = get_lightrag_manager()
                await lightrag_manager.get_client().delete_document(
                    knowledge.collection_name,
                    file.doc_id
                )
                logger.info(f'LightRAG 文档删除成功: {file.doc_id}')
            except Exception as e:
                logger.warning(f'LightRAG 文档删除失败: {e}')
        
        # 删除 MinIO 文件
        try:
            minio_client = MinioClientManager.get_client()
            minio_client.delete_file(file.file_path)
        except Exception as e:
            logger.warning(f'MinIO 文件删除失败: {e}')
        
        # 删除数据库记录
        success = await KnowledgeFileDao.delete_file_by_id(db, file_id)
        if success:
            await db.commit()
            logger.info(f'文件删除成功: {file_id}')
        
        return success
    
    @staticmethod
    async def query_knowledge_by_project(
        db: AsyncSession,
        project_id: int,
        query: str,
        mode: str = 'hybrid',
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        通过项目ID查询知识库（项目与知识库一对一）
        
        通过项目的 workspace（project_{project_id}）进行查询，确保数据隔离。
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            query: 查询文本
            mode: 查询模式 (naive/local/global/hybrid)
            top_k: 返回结果数量
        
        Returns:
            查询结果
        
        Raises:
            ValueError: 项目不存在或知识库未启用
        """
        # 获取项目的知识库（项目与知识库一对一）
        knowledge = await KnowledgeDao.select_knowledge_by_project_id(db, project_id)
        if not knowledge:
            raise ValueError(f'项目 {project_id} 的知识库不存在，请先上传文档')
        
        # 验证知识库状态
        if knowledge.status != '0':
            raise ValueError('知识库未启用')
        
        # 使用项目的 workspace（collection_name）进行查询
        # workspace 格式：project_{project_id}
        # 通过 LIGHTRAG-WORKSPACE header 传递给 anything-chat-rag，确保数据隔离
        workspace = knowledge.collection_name
        
        logger.info(f'查询项目知识库: project_id={project_id}, workspace={workspace}, query: {query[:50]}...')
        
        # 调用 LightRAG 查询（使用 workspace 确保数据隔离）
        lightrag_manager = get_lightrag_manager()
        result = await lightrag_manager.query_knowledge(
            collection_name=workspace,  # 使用 workspace 作为 collection_name
            query=query,
            mode=mode,
            top_k=top_k
        )
        
        # 添加知识库信息
        result['knowledge_id'] = knowledge.knowledge_id
        result['knowledge_name'] = knowledge.knowledge_name
        result['collection_name'] = workspace
        result['project_id'] = project_id
        
        logger.info(f'查询成功: project_id={project_id}, workspace={workspace}')
        
        return result
    
    @staticmethod
    async def query_knowledge(
        db: AsyncSession,
        knowledge_id: int,
        query: str,
        mode: str = 'hybrid',
        top_k: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        查询知识库（支持项目隔离）
        
        通过知识库的 workspace（collection_name）进行查询，确保数据隔离。
        如果提供了 project_id，会验证知识库是否属于指定项目。
        
        Args:
            db: 数据库会话
            knowledge_id: 知识库ID
            query: 查询文本
            mode: 查询模式 (naive/local/global/hybrid)
            top_k: 返回结果数量
            project_id: 项目ID（可选，用于验证数据隔离）
        
        Returns:
            查询结果
        
        Raises:
            ValueError: 知识库不存在、未启用或不属于指定项目
        """
        # 获取知识库信息
        knowledge = await KnowledgeDao.select_knowledge_by_id(db, knowledge_id)
        if not knowledge:
            raise ValueError('知识库不存在')
        
        # 验证知识库状态
        if knowledge.status != '0':
            raise ValueError('知识库未启用')
        
        # 验证项目隔离（如果提供了 project_id）
        if project_id is not None and knowledge.project_id != project_id:
            raise ValueError(f'知识库不属于项目 {project_id}，无法查询')
        
        # 使用知识库的 workspace（collection_name）进行查询
        # collection_name 格式：project_{project_id}
        # 通过 LIGHTRAG-WORKSPACE header 传递给 anything-chat-rag，确保数据隔离
        workspace = knowledge.collection_name
        
        logger.info(f'查询知识库: {knowledge_id}, workspace: {workspace}, query: {query[:50]}...')
        
        # 调用 LightRAG 查询（使用 workspace 确保数据隔离）
        lightrag_manager = get_lightrag_manager()
        result = await lightrag_manager.query_knowledge(
            collection_name=workspace,  # 使用 workspace 作为 collection_name
            query=query,
            mode=mode,
            top_k=top_k
        )
        
        # 添加知识库信息
        result['knowledge_id'] = knowledge_id
        result['knowledge_name'] = knowledge.knowledge_name
        result['collection_name'] = workspace
        result['project_id'] = knowledge.project_id
        
        logger.info(f'查询成功: {knowledge_id}, workspace: {workspace}')
        
        return result


