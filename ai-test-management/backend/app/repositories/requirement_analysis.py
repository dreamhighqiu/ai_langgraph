"""
需求分析 Repository

负责需求分析的数据库操作
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.requirement_analysis import RequirementAnalysis
from app.models.project import Project
from app.models.user import User
from app.schemas.enums import RequirementAnalysisStatus


class RequirementAnalysisRepository:
    """需求分析 Repository"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, requirement_analysis: RequirementAnalysis) -> RequirementAnalysis:
        """创建需求分析"""
        self.db.add(requirement_analysis)
        await self.db.commit()
        await self.db.refresh(requirement_analysis)
        return requirement_analysis
    
    async def get_by_id(self, requirement_analysis_id: UUID) -> Optional[RequirementAnalysis]:
        """根据 ID 获取需求分析"""
        stmt = (
            select(RequirementAnalysis)
            .options(
                selectinload(RequirementAnalysis.project),
                selectinload(RequirementAnalysis.creator),
                selectinload(RequirementAnalysis.owner)
            )
            .where(RequirementAnalysis.id == requirement_analysis_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_identifier(
        self, 
        project_id: UUID, 
        identifier: str
    ) -> Optional[RequirementAnalysis]:
        """根据项目 ID 和标识符获取需求分析"""
        stmt = (
            select(RequirementAnalysis)
            .where(
                and_(
                    RequirementAnalysis.project_id == project_id,
                    RequirementAnalysis.identifier == identifier
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[RequirementAnalysisStatus] = None,
        owner_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> tuple[List[RequirementAnalysis], int]:
        """获取需求分析列表（带分页和过滤）"""
        # 构建基础查询
        stmt = select(RequirementAnalysis).options(
            selectinload(RequirementAnalysis.project),
            selectinload(RequirementAnalysis.creator),
            selectinload(RequirementAnalysis.owner)
        )
        count_stmt = select(func.count()).select_from(RequirementAnalysis)
        
        # 添加过滤条件
        filters = []
        if project_id:
            filters.append(RequirementAnalysis.project_id == project_id)
        if status:
            filters.append(RequirementAnalysis.status == status)
        if owner_id:
            filters.append(RequirementAnalysis.owner_id == owner_id)
        if created_by:
            filters.append(RequirementAnalysis.created_by == created_by)
        if tags:
            # PostgreSQL 的 JSONB 数组包含查询
            for tag in tags:
                filters.append(RequirementAnalysis.tags.contains([tag]))
        if search:
            search_filter = or_(
                RequirementAnalysis.title.ilike(f"%{search}%"),
                RequirementAnalysis.description.ilike(f"%{search}%"),
                RequirementAnalysis.identifier.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))
        
        # 获取总数
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # 添加排序
        order_column = getattr(RequirementAnalysis, order_by, RequirementAnalysis.created_at)
        if order_direction.lower() == "desc":
            stmt = stmt.order_by(order_column.desc())
        else:
            stmt = stmt.order_by(order_column.asc())
        
        # 添加分页
        stmt = stmt.offset(skip).limit(limit)
        
        # 执行查询
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total
    
    async def update(
        self, 
        requirement_analysis: RequirementAnalysis,
        **kwargs
    ) -> RequirementAnalysis:
        """更新需求分析"""
        for key, value in kwargs.items():
            if hasattr(requirement_analysis, key) and value is not None:
                setattr(requirement_analysis, key, value)
        
        await self.db.commit()
        await self.db.refresh(requirement_analysis)
        return requirement_analysis
    
    async def delete(self, requirement_analysis: RequirementAnalysis) -> bool:
        """删除需求分析"""
        await self.db.delete(requirement_analysis)
        await self.db.commit()
        return True
    
    async def get_next_identifier(self, project_id: UUID, prefix: str = "REQ-ANAL") -> str:
        """生成下一个需求分析标识符"""
        # 获取该项目下最大的编号
        stmt = (
            select(func.max(RequirementAnalysis.identifier))
            .where(
                and_(
                    RequirementAnalysis.project_id == project_id,
                    RequirementAnalysis.identifier.like(f"{prefix}-%")
                )
            )
        )
        result = await self.db.execute(stmt)
        max_identifier = result.scalar_one_or_none()
        
        if max_identifier:
            # 提取编号部分并递增
            try:
                number = int(max_identifier.split("-")[-1])
                next_number = number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{prefix}-{next_number:04d}"
    
    async def get_by_project(self, project_id: UUID) -> List[RequirementAnalysis]:
        """获取项目下的所有需求分析"""
        stmt = (
            select(RequirementAnalysis)
            .where(RequirementAnalysis.project_id == project_id)
            .order_by(RequirementAnalysis.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_statistics(self, project_id: UUID) -> dict:
        """获取需求分析统计信息"""
        # 按状态统计
        status_stmt = (
            select(
                RequirementAnalysis.status,
                func.count(RequirementAnalysis.id)
            )
            .where(RequirementAnalysis.project_id == project_id)
            .group_by(RequirementAnalysis.status)
        )
        status_result = await self.db.execute(status_stmt)
        status_stats = {status: count for status, count in status_result.all()}
        
        # 平均质量评分
        avg_score_stmt = (
            select(func.avg(RequirementAnalysis.quality_score))
            .where(
                and_(
                    RequirementAnalysis.project_id == project_id,
                    RequirementAnalysis.quality_score.is_not(None)
                )
            )
        )
        avg_score_result = await self.db.execute(avg_score_stmt)
        avg_quality_score = avg_score_result.scalar_one_or_none() or 0
        
        # 总数
        total_stmt = (
            select(func.count(RequirementAnalysis.id))
            .where(RequirementAnalysis.project_id == project_id)
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one()
        
        return {
            "total": total,
            "status_distribution": status_stats,
            "average_quality_score": round(float(avg_quality_score), 2),
        }
    
    async def bulk_update_status(
        self,
        requirement_analysis_ids: List[UUID],
        status: RequirementAnalysisStatus
    ) -> int:
        """批量更新需求分析状态"""
        stmt = (
            select(RequirementAnalysis)
            .where(RequirementAnalysis.id.in_(requirement_analysis_ids))
        )
        result = await self.db.execute(stmt)
        requirement_analyses = list(result.scalars().all())
        
        for ra in requirement_analyses:
            ra.status = status
        
        await self.db.commit()
        return len(requirement_analyses)
    
    async def search_by_tags(
        self,
        project_id: UUID,
        tags: List[str],
        match_all: bool = False
    ) -> List[RequirementAnalysis]:
        """根据标签搜索需求分析
        
        Args:
            project_id: 项目 ID
            tags: 标签列表
            match_all: True 表示必须匹配所有标签，False 表示匹配任意一个标签
        """
        stmt = select(RequirementAnalysis).where(
            RequirementAnalysis.project_id == project_id
        )
        
        if match_all:
            # 必须包含所有标签
            for tag in tags:
                stmt = stmt.where(RequirementAnalysis.tags.contains([tag]))
        else:
            # 包含任意一个标签
            tag_filters = [RequirementAnalysis.tags.contains([tag]) for tag in tags]
            stmt = stmt.where(or_(*tag_filters))
        
        stmt = stmt.order_by(RequirementAnalysis.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

