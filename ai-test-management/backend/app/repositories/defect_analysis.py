"""
缺陷分析 Repository

负责缺陷分析的数据库操作
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.defect_analysis import DefectAnalysis
from app.models.project import Project
from app.models.user import User
from app.schemas.enums import (
    DefectAnalysisStatus,
    DefectSeverity,
    DefectPriority,
    DefectType
)


class DefectAnalysisRepository:
    """缺陷分析 Repository"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, defect_analysis: DefectAnalysis) -> DefectAnalysis:
        """创建缺陷分析"""
        self.db.add(defect_analysis)
        await self.db.commit()
        await self.db.refresh(defect_analysis)
        return defect_analysis
    
    async def get_by_id(self, defect_analysis_id: UUID) -> Optional[DefectAnalysis]:
        """根据 ID 获取缺陷分析"""
        stmt = (
            select(DefectAnalysis)
            .options(
                selectinload(DefectAnalysis.project),
                selectinload(DefectAnalysis.creator),
                selectinload(DefectAnalysis.owner)
            )
            .where(DefectAnalysis.id == defect_analysis_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_identifier(
        self, 
        project_id: UUID, 
        identifier: str
    ) -> Optional[DefectAnalysis]:
        """根据项目 ID 和标识符获取缺陷分析"""
        stmt = (
            select(DefectAnalysis)
            .where(
                and_(
                    DefectAnalysis.project_id == project_id,
                    DefectAnalysis.identifier == identifier
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[DefectAnalysisStatus] = None,
        severity: Optional[DefectSeverity] = None,
        priority: Optional[DefectPriority] = None,
        defect_type: Optional[DefectType] = None,
        owner_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> tuple[List[DefectAnalysis], int]:
        """获取缺陷分析列表（带分页和过滤）"""
        # 构建基础查询
        stmt = select(DefectAnalysis).options(
            selectinload(DefectAnalysis.project),
            selectinload(DefectAnalysis.creator),
            selectinload(DefectAnalysis.owner)
        )
        count_stmt = select(func.count()).select_from(DefectAnalysis)
        
        # 添加过滤条件
        filters = []
        if project_id:
            filters.append(DefectAnalysis.project_id == project_id)
        if status:
            filters.append(DefectAnalysis.status == status)
        if severity:
            filters.append(DefectAnalysis.severity == severity)
        if priority:
            filters.append(DefectAnalysis.priority == priority)
        if defect_type:
            filters.append(DefectAnalysis.defect_type == defect_type)
        if owner_id:
            filters.append(DefectAnalysis.owner_id == owner_id)
        if created_by:
            filters.append(DefectAnalysis.created_by == created_by)
        if tags:
            # PostgreSQL 的 JSONB 数组包含查询
            for tag in tags:
                filters.append(DefectAnalysis.tags.contains([tag]))
        if search:
            search_filter = or_(
                DefectAnalysis.title.ilike(f"%{search}%"),
                DefectAnalysis.description.ilike(f"%{search}%"),
                DefectAnalysis.identifier.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))
        
        # 获取总数
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # 添加排序
        order_column = getattr(DefectAnalysis, order_by, DefectAnalysis.created_at)
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
        defect_analysis: DefectAnalysis,
        **kwargs
    ) -> DefectAnalysis:
        """更新缺陷分析"""
        for key, value in kwargs.items():
            if hasattr(defect_analysis, key) and value is not None:
                setattr(defect_analysis, key, value)
        
        await self.db.commit()
        await self.db.refresh(defect_analysis)
        return defect_analysis
    
    async def delete(self, defect_analysis: DefectAnalysis) -> bool:
        """删除缺陷分析"""
        await self.db.delete(defect_analysis)
        await self.db.commit()
        return True
    
    async def get_next_identifier(self, project_id: UUID, prefix: str = "DEF-ANAL") -> str:
        """生成下一个缺陷分析标识符"""
        # 获取该项目下最大的编号
        stmt = (
            select(func.max(DefectAnalysis.identifier))
            .where(
                and_(
                    DefectAnalysis.project_id == project_id,
                    DefectAnalysis.identifier.like(f"{prefix}-%")
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
    
    async def get_by_project(self, project_id: UUID) -> List[DefectAnalysis]:
        """获取项目下的所有缺陷分析"""
        stmt = (
            select(DefectAnalysis)
            .where(DefectAnalysis.project_id == project_id)
            .order_by(DefectAnalysis.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_statistics(self, project_id: UUID) -> dict:
        """获取缺陷分析统计信息"""
        # 按状态统计
        status_stmt = (
            select(
                DefectAnalysis.status,
                func.count(DefectAnalysis.id)
            )
            .where(DefectAnalysis.project_id == project_id)
            .group_by(DefectAnalysis.status)
        )
        status_result = await self.db.execute(status_stmt)
        status_stats = {status: count for status, count in status_result.all()}
        
        # 按严重程度统计
        severity_stmt = (
            select(
                DefectAnalysis.severity,
                func.count(DefectAnalysis.id)
            )
            .where(DefectAnalysis.project_id == project_id)
            .group_by(DefectAnalysis.severity)
        )
        severity_result = await self.db.execute(severity_stmt)
        severity_stats = {severity: count for severity, count in severity_result.all()}
        
        # 按优先级统计
        priority_stmt = (
            select(
                DefectAnalysis.priority,
                func.count(DefectAnalysis.id)
            )
            .where(DefectAnalysis.project_id == project_id)
            .group_by(DefectAnalysis.priority)
        )
        priority_result = await self.db.execute(priority_stmt)
        priority_stats = {priority: count for priority, count in priority_result.all()}
        
        # 按类型统计
        type_stmt = (
            select(
                DefectAnalysis.defect_type,
                func.count(DefectAnalysis.id)
            )
            .where(DefectAnalysis.project_id == project_id)
            .group_by(DefectAnalysis.defect_type)
        )
        type_result = await self.db.execute(type_stmt)
        type_stats = {defect_type: count for defect_type, count in type_result.all()}
        
        # 平均质量评分
        avg_score_stmt = (
            select(func.avg(DefectAnalysis.quality_score))
            .where(
                and_(
                    DefectAnalysis.project_id == project_id,
                    DefectAnalysis.quality_score.is_not(None)
                )
            )
        )
        avg_score_result = await self.db.execute(avg_score_stmt)
        avg_quality_score = avg_score_result.scalar_one_or_none() or 0
        
        # 总数
        total_stmt = (
            select(func.count(DefectAnalysis.id))
            .where(DefectAnalysis.project_id == project_id)
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one()
        
        return {
            "total": total,
            "status_distribution": status_stats,
            "severity_distribution": severity_stats,
            "priority_distribution": priority_stats,
            "type_distribution": type_stats,
            "average_quality_score": round(float(avg_quality_score), 2),
        }
    
    async def bulk_update_status(
        self,
        defect_analysis_ids: List[UUID],
        status: DefectAnalysisStatus
    ) -> int:
        """批量更新缺陷分析状态"""
        stmt = (
            select(DefectAnalysis)
            .where(DefectAnalysis.id.in_(defect_analysis_ids))
        )
        result = await self.db.execute(stmt)
        defect_analyses = list(result.scalars().all())
        
        for da in defect_analyses:
            da.status = status
        
        await self.db.commit()
        return len(defect_analyses)
    
    async def search_by_tags(
        self,
        project_id: UUID,
        tags: List[str],
        match_all: bool = False
    ) -> List[DefectAnalysis]:
        """根据标签搜索缺陷分析
        
        Args:
            project_id: 项目 ID
            tags: 标签列表
            match_all: True 表示必须匹配所有标签，False 表示匹配任意一个标签
        """
        stmt = select(DefectAnalysis).where(
            DefectAnalysis.project_id == project_id
        )
        
        if match_all:
            # 必须包含所有标签
            for tag in tags:
                stmt = stmt.where(DefectAnalysis.tags.contains([tag]))
        else:
            # 包含任意一个标签
            tag_filters = [DefectAnalysis.tags.contains([tag]) for tag in tags]
            stmt = stmt.where(or_(*tag_filters))
        
        stmt = stmt.order_by(DefectAnalysis.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_high_priority_defects(
        self,
        project_id: UUID,
        limit: int = 10
    ) -> List[DefectAnalysis]:
        """获取高优先级缺陷（紧急或高优先级，严重或关键严重程度）"""
        stmt = (
            select(DefectAnalysis)
            .where(
                and_(
                    DefectAnalysis.project_id == project_id,
                    or_(
                        DefectAnalysis.priority.in_([DefectPriority.URGENT, DefectPriority.HIGH]),
                        DefectAnalysis.severity.in_([DefectSeverity.CRITICAL, DefectSeverity.HIGH])
                    ),
                    DefectAnalysis.status.in_([
                        DefectAnalysisStatus.DRAFT,
                        DefectAnalysisStatus.IN_REVIEW,
                        DefectAnalysisStatus.APPROVED
                    ])
                )
            )
            .order_by(DefectAnalysis.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

