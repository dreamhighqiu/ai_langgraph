"""
需求分析服务层

处理需求分析的业务逻辑
"""

import asyncio
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.requirement_analysis import RequirementAnalysis
from app.models.user import User
from app.repositories.requirement_analysis import RequirementAnalysisRepository
from app.repositories.user_repo import UserRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.requirement_analysis import (
    RequirementAnalysisCreate,
    RequirementAnalysisUpdate,
    RequirementAnalysisInfo,
    RequirementAnalysisMinifiedInfo,
    RequirementAnalysisDownloadResponse
)
from app.schemas.enums import RequirementAnalysisStatus
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException
)

logger = logging.getLogger(__name__)


class RequirementAnalysisService:
    """需求分析服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = RequirementAnalysisRepository(db)
        self.user_repository = UserRepository(db)
        self.project_repository = ProjectRepository(db)
    
    async def create_requirement_analysis(
        self,
        project_id: UUID,
        data: RequirementAnalysisCreate,
        current_user: User
    ) -> RequirementAnalysisInfo:
        """创建需求分析"""
        # 验证项目是否存在
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"项目不存在: {project_id}")
        
        # 生成需求分析标识符
        identifier = await self.repository.get_next_identifier(project_id)
        
        # 创建需求分析对象
        requirement_analysis = RequirementAnalysis(
            project_id=project_id,
            identifier=identifier,
            title=data.title,
            description=data.description,
            document_url=data.document_url,
            document_type=data.document_type,
            tags=data.tags or [],
            owner_id=data.owner_id,
            created_by=current_user.id,
            status=RequirementAnalysisStatus.DRAFT,
            used_rag=data.use_rag,
            version=1,
        )
        
        # 保存到数据库
        requirement_analysis = await self.repository.create(requirement_analysis)
        
        logger.info(f"创建需求分析成功: {identifier} (ID: {requirement_analysis.id})")
        
        return RequirementAnalysisInfo.model_validate(requirement_analysis)
    
    async def get_requirement_analysis(
        self,
        requirement_analysis_id: UUID,
        current_user: User
    ) -> RequirementAnalysisInfo:
        """获取需求分析详情"""
        requirement_analysis = await self.repository.get_by_id(requirement_analysis_id)
        
        if not requirement_analysis:
            raise NotFoundException(f"需求分析不存在: {requirement_analysis_id}")
        
        return RequirementAnalysisInfo.model_validate(requirement_analysis)
    
    async def update_requirement_analysis(
        self,
        requirement_analysis_id: UUID,
        data: RequirementAnalysisUpdate,
        current_user: User
    ) -> RequirementAnalysisInfo:
        """更新需求分析"""
        requirement_analysis = await self.repository.get_by_id(requirement_analysis_id)
        
        if not requirement_analysis:
            raise NotFoundException(f"需求分析不存在: {requirement_analysis_id}")
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        # 如果状态改变，增加版本号
        if "status" in update_data and update_data["status"] != requirement_analysis.status:
            update_data["version"] = requirement_analysis.version + 1
        
        requirement_analysis = await self.repository.update(
            requirement_analysis,
            **update_data
        )
        
        logger.info(f"更新需求分析成功: {requirement_analysis.identifier}")
        
        return RequirementAnalysisInfo.model_validate(requirement_analysis)
    
    async def delete_requirement_analysis(
        self,
        requirement_analysis_id: UUID,
        current_user: User
    ) -> bool:
        """删除需求分析"""
        requirement_analysis = await self.repository.get_by_id(requirement_analysis_id)
        
        if not requirement_analysis:
            raise NotFoundException(f"需求分析不存在: {requirement_analysis_id}")
        
        # 检查权限（可选：只有创建者或管理员可以删除）
        # if requirement_analysis.created_by != current_user.id and not current_user.is_admin:
        #     raise UnauthorizedException("没有权限删除此需求分析")
        
        await self.repository.delete(requirement_analysis)
        
        logger.info(f"删除需求分析成功: {requirement_analysis.identifier}")
        
        return True
    
    async def list_requirement_analyses(
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
    ) -> tuple[List[RequirementAnalysisMinifiedInfo], int]:
        """获取需求分析列表"""
        requirement_analyses, total = await self.repository.get_list(
            project_id=project_id,
            status=status,
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
            RequirementAnalysisMinifiedInfo.model_validate(ra)
            for ra in requirement_analyses
        ]
        
        return items, total
    
    async def get_project_requirement_analyses(
        self,
        project_id: UUID
    ) -> List[RequirementAnalysisMinifiedInfo]:
        """获取项目的所有需求分析"""
        requirement_analyses = await self.repository.get_by_project(project_id)
        
        return [
            RequirementAnalysisMinifiedInfo.model_validate(ra)
            for ra in requirement_analyses
        ]
    
    async def get_statistics(self, project_id: UUID) -> dict:
        """获取需求分析统计信息"""
        return await self.repository.get_statistics(project_id)
    
    async def update_status(
        self,
        requirement_analysis_id: UUID,
        status: RequirementAnalysisStatus,
        current_user: User
    ) -> RequirementAnalysisInfo:
        """更新需求分析状态"""
        requirement_analysis = await self.repository.get_by_id(requirement_analysis_id)
        
        if not requirement_analysis:
            raise NotFoundException(f"需求分析不存在: {requirement_analysis_id}")
        
        # 更新状态和版本号
        requirement_analysis = await self.repository.update(
            requirement_analysis,
            status=status,
            version=requirement_analysis.version + 1
        )
        
        logger.info(
            f"更新需求分析状态: {requirement_analysis.identifier} -> {status}"
        )
        
        return RequirementAnalysisInfo.model_validate(requirement_analysis)
    
    async def bulk_update_status(
        self,
        requirement_analysis_ids: List[UUID],
        status: RequirementAnalysisStatus,
        current_user: User
    ) -> int:
        """批量更新需求分析状态"""
        count = await self.repository.bulk_update_status(
            requirement_analysis_ids,
            status
        )
        
        logger.info(f"批量更新 {count} 个需求分析状态 -> {status}")
        
        return count
    
    async def search_by_tags(
        self,
        project_id: UUID,
        tags: List[str],
        match_all: bool = False
    ) -> List[RequirementAnalysisMinifiedInfo]:
        """根据标签搜索需求分析"""
        requirement_analyses = await self.repository.search_by_tags(
            project_id,
            tags,
            match_all
        )
        
        return [
            RequirementAnalysisMinifiedInfo.model_validate(ra)
            for ra in requirement_analyses
        ]
    
    async def generate_download_url(
        self,
        requirement_analysis_id: UUID,
        format: str = "pdf"
    ) -> RequirementAnalysisDownloadResponse:
        """生成需求分析报告下载链接
        
        Args:
            requirement_analysis_id: 需求分析 ID
            format: 报告格式（pdf/word/markdown）
        
        Returns:
            下载响应信息
        """
        requirement_analysis = await self.repository.get_by_id(requirement_analysis_id)
        
        if not requirement_analysis:
            raise NotFoundException(f"需求分析不存在: {requirement_analysis_id}")
        
        # TODO: 实现报告生成逻辑
        # 这里应该调用报告生成服务，生成 PDF/Word 等格式的报告
        # 并上传到 MinIO，返回下载链接
        
        # 示例返回（实际实现需要调用报告生成服务）
        return RequirementAnalysisDownloadResponse(
            success=True,
            download_url=f"https://minio.example.com/reports/{requirement_analysis.identifier}.{format}",
            file_name=f"{requirement_analysis.identifier}_需求分析报告.{format}",
            file_size=1048576,  # 示例大小
            message="报告生成成功"
        )
    
    async def trigger_ai_analysis(
        self,
        requirement_analysis_id: UUID,
        document_content: Optional[str] = None,
        use_rag: bool = False,
        rag_query: Optional[str] = None
    ) -> dict:
        """触发 AI 智能分析
        
        Args:
            requirement_analysis_id: 需求分析 ID
            document_content: 文档内容
            use_rag: 是否使用 RAG
            rag_query: RAG 查询
        
        Returns:
            分析任务信息
        """
        requirement_analysis = await self.repository.get_by_id(requirement_analysis_id)
        
        if not requirement_analysis:
            raise NotFoundException(f"需求分析不存在: {requirement_analysis_id}")
        
        # TODO: 调用 LangGraph 智能体进行分析
        # 这里应该调用需求分析智能体，传入文档内容和配置
        # 智能体会异步处理并保存分析结果
        
        logger.info(
            f"触发需求分析任务: {requirement_analysis.identifier}, "
            f"use_rag={use_rag}"
        )
        
        return {
            "success": True,
            "requirement_analysis_id": str(requirement_analysis_id),
            "message": "需求分析任务已启动",
            "status": "processing"
        }

