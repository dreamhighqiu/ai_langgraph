"""
缺陷分析服务层

处理缺陷分析的业务逻辑
"""

import asyncio
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.defect_analysis import DefectAnalysis
from app.models.user import User
from app.repositories.defect_analysis import DefectAnalysisRepository
from app.repositories.user import UserRepository
from app.repositories.project import ProjectRepository
from app.schemas.defect_analysis import (
    DefectAnalysisCreate,
    DefectAnalysisUpdate,
    DefectAnalysisInfo,
    DefectAnalysisMinifiedInfo,
    DefectAnalysisDownloadResponse
)
from app.schemas.enums import (
    DefectAnalysisStatus,
    DefectSeverity,
    DefectPriority,
    DefectType
)
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException
)

logger = logging.getLogger(__name__)


class DefectAnalysisService:
    """缺陷分析服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DefectAnalysisRepository(db)
        self.user_repository = UserRepository(db)
        self.project_repository = ProjectRepository(db)
    
    async def create_defect_analysis(
        self,
        project_id: UUID,
        data: DefectAnalysisCreate,
        current_user: User
    ) -> DefectAnalysisInfo:
        """创建缺陷分析"""
        # 验证项目是否存在
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"项目不存在: {project_id}")
        
        # 生成缺陷分析标识符
        identifier = await self.repository.get_next_identifier(project_id)
        
        # 创建缺陷分析对象
        defect_analysis = DefectAnalysis(
            project_id=project_id,
            identifier=identifier,
            title=data.title,
            description=data.description,
            document_url=data.document_url,
            document_type=data.document_type,
            severity=data.severity,
            priority=data.priority,
            defect_type=data.defect_type,
            tags=data.tags or [],
            owner_id=data.owner_id,
            created_by=current_user.id,
            status=DefectAnalysisStatus.DRAFT,
            used_rag=data.use_rag,
            version=1,
            related_requirement_ids=data.related_requirement_ids or [],
            related_testcase_ids=data.related_testcase_ids or [],
        )
        
        # 保存到数据库
        defect_analysis = await self.repository.create(defect_analysis)
        
        logger.info(f"创建缺陷分析成功: {identifier} (ID: {defect_analysis.id})")
        
        return DefectAnalysisInfo.model_validate(defect_analysis)
    
    async def get_defect_analysis(
        self,
        defect_analysis_id: UUID,
        current_user: User
    ) -> DefectAnalysisInfo:
        """获取缺陷分析详情"""
        defect_analysis = await self.repository.get_by_id(defect_analysis_id)
        
        if not defect_analysis:
            raise NotFoundException(f"缺陷分析不存在: {defect_analysis_id}")
        
        return DefectAnalysisInfo.model_validate(defect_analysis)
    
    async def update_defect_analysis(
        self,
        defect_analysis_id: UUID,
        data: DefectAnalysisUpdate,
        current_user: User
    ) -> DefectAnalysisInfo:
        """更新缺陷分析"""
        defect_analysis = await self.repository.get_by_id(defect_analysis_id)
        
        if not defect_analysis:
            raise NotFoundException(f"缺陷分析不存在: {defect_analysis_id}")
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        # 如果状态改变，增加版本号
        if "status" in update_data and update_data["status"] != defect_analysis.status:
            update_data["version"] = defect_analysis.version + 1
        
        defect_analysis = await self.repository.update(
            defect_analysis,
            **update_data
        )
        
        logger.info(f"更新缺陷分析成功: {defect_analysis.identifier}")
        
        return DefectAnalysisInfo.model_validate(defect_analysis)
    
    async def delete_defect_analysis(
        self,
        defect_analysis_id: UUID,
        current_user: User
    ) -> bool:
        """删除缺陷分析"""
        defect_analysis = await self.repository.get_by_id(defect_analysis_id)
        
        if not defect_analysis:
            raise NotFoundException(f"缺陷分析不存在: {defect_analysis_id}")
        
        # 检查权限（可选：只有创建者或管理员可以删除）
        # if defect_analysis.created_by != current_user.id and not current_user.is_admin:
        #     raise UnauthorizedException("没有权限删除此缺陷分析")
        
        await self.repository.delete(defect_analysis)
        
        logger.info(f"删除缺陷分析成功: {defect_analysis.identifier}")
        
        return True
    
    async def list_defect_analyses(
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
    ) -> tuple[List[DefectAnalysisMinifiedInfo], int]:
        """获取缺陷分析列表"""
        defect_analyses, total = await self.repository.get_list(
            project_id=project_id,
            status=status,
            severity=severity,
            priority=priority,
            defect_type=defect_type,
            owner_id=owner_id,
            created_by=created_by,
            tags=tags,
            search=search,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_direction=order_direction
        )
        
        # 转换为精简信息
        items = [
            DefectAnalysisMinifiedInfo.model_validate(da)
            for da in defect_analyses
        ]
        
        return items, total
    
    async def get_project_defect_analyses(
        self,
        project_id: UUID
    ) -> List[DefectAnalysisMinifiedInfo]:
        """获取项目的所有缺陷分析"""
        defect_analyses = await self.repository.get_by_project(project_id)
        
        return [
            DefectAnalysisMinifiedInfo.model_validate(da)
            for da in defect_analyses
        ]
    
    async def get_statistics(self, project_id: UUID) -> dict:
        """获取缺陷分析统计信息"""
        return await self.repository.get_statistics(project_id)
    
    async def update_status(
        self,
        defect_analysis_id: UUID,
        status: DefectAnalysisStatus,
        current_user: User
    ) -> DefectAnalysisInfo:
        """更新缺陷分析状态"""
        defect_analysis = await self.repository.get_by_id(defect_analysis_id)
        
        if not defect_analysis:
            raise NotFoundException(f"缺陷分析不存在: {defect_analysis_id}")
        
        # 更新状态和版本号
        defect_analysis = await self.repository.update(
            defect_analysis,
            status=status,
            version=defect_analysis.version + 1
        )
        
        logger.info(
            f"更新缺陷分析状态: {defect_analysis.identifier} -> {status}"
        )
        
        return DefectAnalysisInfo.model_validate(defect_analysis)
    
    async def bulk_update_status(
        self,
        defect_analysis_ids: List[UUID],
        status: DefectAnalysisStatus,
        current_user: User
    ) -> int:
        """批量更新缺陷分析状态"""
        count = await self.repository.bulk_update_status(
            defect_analysis_ids,
            status
        )
        
        logger.info(f"批量更新 {count} 个缺陷分析状态 -> {status}")
        
        return count
    
    async def search_by_tags(
        self,
        project_id: UUID,
        tags: List[str],
        match_all: bool = False
    ) -> List[DefectAnalysisMinifiedInfo]:
        """根据标签搜索缺陷分析"""
        defect_analyses = await self.repository.search_by_tags(
            project_id,
            tags,
            match_all
        )
        
        return [
            DefectAnalysisMinifiedInfo.model_validate(da)
            for da in defect_analyses
        ]
    
    async def get_high_priority_defects(
        self,
        project_id: UUID,
        limit: int = 10
    ) -> List[DefectAnalysisMinifiedInfo]:
        """获取高优先级缺陷"""
        defect_analyses = await self.repository.get_high_priority_defects(
            project_id,
            limit
        )
        
        return [
            DefectAnalysisMinifiedInfo.model_validate(da)
            for da in defect_analyses
        ]
    
    async def generate_download_url(
        self,
        defect_analysis_id: UUID,
        format: str = "pdf"
    ) -> DefectAnalysisDownloadResponse:
        """生成缺陷分析报告下载链接
        
        Args:
            defect_analysis_id: 缺陷分析 ID
            format: 报告格式（pdf/word/markdown）
        
        Returns:
            下载响应信息
        """
        defect_analysis = await self.repository.get_by_id(defect_analysis_id)
        
        if not defect_analysis:
            raise NotFoundException(f"缺陷分析不存在: {defect_analysis_id}")
        
        # TODO: 实现报告生成逻辑
        # 这里应该调用报告生成服务，生成 PDF/Word 等格式的报告
        # 并上传到 MinIO，返回下载链接
        
        # 示例返回（实际实现需要调用报告生成服务）
        return DefectAnalysisDownloadResponse(
            success=True,
            download_url=f"https://minio.example.com/reports/{defect_analysis.identifier}.{format}",
            file_name=f"{defect_analysis.identifier}_缺陷分析报告.{format}",
            file_size=1048576,  # 示例大小
            message="报告生成成功"
        )
    
    async def trigger_ai_analysis(
        self,
        defect_analysis_id: UUID,
        document_content: Optional[str] = None,
        use_rag: bool = False,
        rag_query: Optional[str] = None
    ) -> dict:
        """触发 AI 智能分析
        
        Args:
            defect_analysis_id: 缺陷分析 ID
            document_content: 文档内容
            use_rag: 是否使用 RAG
            rag_query: RAG 查询
        
        Returns:
            分析任务信息
        """
        defect_analysis = await self.repository.get_by_id(defect_analysis_id)
        
        if not defect_analysis:
            raise NotFoundException(f"缺陷分析不存在: {defect_analysis_id}")
        
        # TODO: 调用 LangGraph 智能体进行分析
        # 这里应该调用缺陷分析智能体，传入文档内容和配置
        # 智能体会异步处理并保存分析结果
        
        logger.info(
            f"触发缺陷分析任务: {defect_analysis.identifier}, "
            f"use_rag={use_rag}"
        )
        
        return {
            "success": True,
            "defect_analysis_id": str(defect_analysis_id),
            "message": "缺陷分析任务已启动",
            "status": "processing"
        }

