"""
知识库数据访问对象（DAO）
"""
from typing import Optional, Tuple, List

from sqlalchemy import and_, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.knowledge_do import TestKnowledge, TestKnowledgeFile
from module_testing.entity.vo.knowledge_vo import KnowledgeQueryModel, KnowledgeFileQueryModel


class KnowledgeDao:
    """知识库 DAO"""
    
    @staticmethod
    async def select_knowledge_by_id(db: AsyncSession, knowledge_id: int) -> Optional[TestKnowledge]:
        """根据ID查询知识库"""
        result = await db.execute(
            select(TestKnowledge).where(TestKnowledge.knowledge_id == knowledge_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def select_knowledge_by_collection(db: AsyncSession, collection_name: str) -> Optional[TestKnowledge]:
        """根据 Collection 名称查询知识库"""
        result = await db.execute(
            select(TestKnowledge).where(TestKnowledge.collection_name == collection_name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def select_knowledge_by_project_id(db: AsyncSession, project_id: int) -> Optional[TestKnowledge]:
        """
        根据项目ID查询知识库（项目与知识库一对一）
        
        如果项目有多个知识库，返回第一个（按创建时间排序，最新的优先）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
        
        Returns:
            知识库对象或None
        """
        result = await db.execute(
            select(TestKnowledge)
            .where(TestKnowledge.project_id == project_id)
            .order_by(TestKnowledge.create_time.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def select_knowledge_list_by_project_id(db: AsyncSession, project_id: int) -> List[TestKnowledge]:
        """
        根据项目ID查询所有知识库（用于数据清理）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
        
        Returns:
            知识库列表
        """
        result = await db.execute(
            select(TestKnowledge)
            .where(TestKnowledge.project_id == project_id)
            .order_by(TestKnowledge.create_time.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def select_knowledge_by_collection_name(
        db: AsyncSession,
        collection_name: str,
        exclude_knowledge_id: Optional[int] = None
    ) -> Optional[TestKnowledge]:
        """
        根据 Collection 名称查询知识库（可排除指定ID）
        
        Args:
            db: 数据库会话
            collection_name: Collection 名称
            exclude_knowledge_id: 排除的知识库ID（用于更新时检查重名）
        
        Returns:
            知识库对象或None
        """
        conditions = [TestKnowledge.collection_name == collection_name]
        if exclude_knowledge_id:
            conditions.append(TestKnowledge.knowledge_id != exclude_knowledge_id)
        
        result = await db.execute(
            select(TestKnowledge).where(and_(*conditions))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def select_knowledge_list(
        db: AsyncSession,
        query: KnowledgeQueryModel
    ) -> Tuple[List[TestKnowledge], int]:
        """查询知识库列表"""
        conditions = []
        
        if query.project_id:
            conditions.append(TestKnowledge.project_id == query.project_id)
        if query.knowledge_name:
            conditions.append(TestKnowledge.knowledge_name.like(f'%{query.knowledge_name}%'))
        if query.status:
            conditions.append(TestKnowledge.status == query.status)
        
        # 查询总数
        count_query = select(func.count(TestKnowledge.knowledge_id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        list_query = (
            select(TestKnowledge)
            .where(and_(*conditions))
            .order_by(TestKnowledge.create_time.desc())
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
        result = await db.execute(list_query)
        knowledge_list = result.scalars().all()
        
        return list(knowledge_list), total
    
    @staticmethod
    async def insert_knowledge(db: AsyncSession, knowledge: TestKnowledge) -> TestKnowledge:
        """插入知识库"""
        db.add(knowledge)
        await db.flush()
        await db.refresh(knowledge)
        return knowledge
    
    @staticmethod
    async def update_knowledge_by_id(db: AsyncSession, knowledge_id: int, **kwargs) -> bool:
        """更新知识库"""
        result = await db.execute(
            update(TestKnowledge)
            .where(TestKnowledge.knowledge_id == knowledge_id)
            .values(**kwargs)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_knowledge_by_id(db: AsyncSession, knowledge_id: int) -> bool:
        """删除知识库"""
        result = await db.execute(
            delete(TestKnowledge).where(TestKnowledge.knowledge_id == knowledge_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def update_knowledge_stats(
        db: AsyncSession,
        knowledge_id: int,
        file_count: int,
        vector_count: int
    ) -> bool:
        """更新知识库统计信息"""
        return await KnowledgeDao.update_knowledge_by_id(
            db,
            knowledge_id,
            file_count=file_count,
            vector_count=vector_count
        )


class KnowledgeFileDao:
    """知识库文件 DAO"""
    
    @staticmethod
    async def select_file_by_id(db: AsyncSession, file_id: int) -> Optional[TestKnowledgeFile]:
        """根据ID查询文件"""
        result = await db.execute(
            select(TestKnowledgeFile).where(TestKnowledgeFile.file_id == file_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def select_file_list(
        db: AsyncSession,
        query: KnowledgeFileQueryModel
    ) -> Tuple[List[TestKnowledgeFile], int]:
        """查询文件列表"""
        conditions = []
        
        if query.knowledge_id:
            conditions.append(TestKnowledgeFile.knowledge_id == query.knowledge_id)
        if query.file_name:
            conditions.append(TestKnowledgeFile.file_name.like(f'%{query.file_name}%'))
        if query.process_status:
            conditions.append(TestKnowledgeFile.process_status == query.process_status)
        
        # 查询总数
        count_query = select(func.count(TestKnowledgeFile.file_id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        list_query = (
            select(TestKnowledgeFile)
            .where(and_(*conditions))
            .order_by(TestKnowledgeFile.create_time.desc())
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
        result = await db.execute(list_query)
        file_list = result.scalars().all()
        
        return list(file_list), total
    
    @staticmethod
    async def insert_file(db: AsyncSession, file: TestKnowledgeFile) -> TestKnowledgeFile:
        """插入文件"""
        db.add(file)
        await db.flush()
        await db.refresh(file)
        return file
    
    @staticmethod
    async def update_file_status(
        db: AsyncSession,
        file_id: int,
        status: str,
        progress: int = None,
        error_msg: str = None
    ) -> bool:
        """更新文件处理状态"""
        update_data = {'process_status': status}
        if progress is not None:
            update_data['process_progress'] = progress
        if error_msg is not None:
            update_data['error_msg'] = error_msg
        if status == 'processing' and progress is None:
            from datetime import datetime
            update_data['process_start_time'] = datetime.now()
        if status in ['completed', 'failed']:
            from datetime import datetime
            update_data['process_end_time'] = datetime.now()
        
        result = await db.execute(
            update(TestKnowledgeFile)
            .where(TestKnowledgeFile.file_id == file_id)
            .values(**update_data)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_file_by_id(db: AsyncSession, file_id: int) -> bool:
        """删除文件"""
        result = await db.execute(
            delete(TestKnowledgeFile).where(TestKnowledgeFile.file_id == file_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_files_by_knowledge_id(db: AsyncSession, knowledge_id: int) -> int:
        """删除知识库下所有文件"""
        result = await db.execute(
            delete(TestKnowledgeFile).where(TestKnowledgeFile.knowledge_id == knowledge_id)
        )
        return result.rowcount
    
    @staticmethod
    async def get_knowledge_stats(db: AsyncSession, knowledge_id: int) -> dict:
        """获取知识库统计信息"""
        # 文件总数
        file_count_query = select(func.count(TestKnowledgeFile.file_id)).where(
            TestKnowledgeFile.knowledge_id == knowledge_id
        )
        file_count_result = await db.execute(file_count_query)
        file_count = file_count_result.scalar() or 0
        
        # 向量总数
        vector_count_query = select(func.sum(TestKnowledgeFile.vector_count)).where(
            TestKnowledgeFile.knowledge_id == knowledge_id
        )
        vector_count_result = await db.execute(vector_count_query)
        vector_count = vector_count_result.scalar() or 0
        
        # 各状态文件数
        status_counts = {}
        for status in ['pending', 'processing', 'completed', 'failed']:
            status_query = select(func.count(TestKnowledgeFile.file_id)).where(
                and_(
                    TestKnowledgeFile.knowledge_id == knowledge_id,
                    TestKnowledgeFile.process_status == status
                )
            )
            status_result = await db.execute(status_query)
            status_counts[f'{status}_count'] = status_result.scalar() or 0
        
        return {
            'file_count': file_count,
            'vector_count': vector_count,
            **status_counts
        }


