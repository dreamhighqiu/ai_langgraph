"""
需求分析 API 端点

提供需求分析的 RESTful API 接口
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSessionDep, CurrentUserIdDep
from app.config.database import get_db
from app.services.requirement_analysis_service import RequirementAnalysisService
from app.schemas.requirement_analysis import (
    RequirementAnalysisCreate,
    RequirementAnalysisUpdate,
    RequirementAnalysisInfo,
    RequirementAnalysisMinifiedInfo,
    RequirementAnalysisDownloadResponse
)
from app.schemas.enums import RequirementAnalysisStatus
from app.schemas.common import SuccessResponse, MessageResponse, Response
from app.schemas.pagination import PaginatedResponse, PaginationInfo
from app.utils.exceptions import UnauthorizedException

router = APIRouter(prefix="/requirement-analysis", tags=["需求分析"])


async def _get_current_user(
    service: RequirementAnalysisService,
    current_user_id: UUID,
):
    current_user = await service.user_repository.get_by_id(current_user_id)
    if not current_user:
        raise UnauthorizedException()
    return current_user


@router.post(
    "/projects/{project_id}/requirement-analysis",
    response_model=Response[RequirementAnalysisInfo],
    status_code=status.HTTP_201_CREATED,
    summary="创建需求分析",
    description="为指定项目创建新的需求分析记录"
)
async def create_requirement_analysis(
    project_id: UUID,
    data: RequirementAnalysisCreate,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """创建需求分析"""
    service = RequirementAnalysisService(db)
    current_user = await _get_current_user(service, current_user_id)
    result = await service.create_requirement_analysis(
        project_id=project_id,
        data=data,
        current_user=current_user
    )
    return Response(data=result, message="需求分析创建成功")


@router.get(
    "/{requirement_analysis_id}",
    response_model=Response[RequirementAnalysisInfo],
    summary="获取需求分析详情",
    description="根据 ID 获取需求分析的详细信息"
)
async def get_requirement_analysis(
    requirement_analysis_id: UUID,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """获取需求分析详情"""
    service = RequirementAnalysisService(db)
    current_user = await _get_current_user(service, current_user_id)
    result = await service.get_requirement_analysis(
        requirement_analysis_id=requirement_analysis_id,
        current_user=current_user
    )
    return Response(data=result)


@router.put(
    "/{requirement_analysis_id}",
    response_model=Response[RequirementAnalysisInfo],
    summary="更新需求分析",
    description="更新需求分析的信息"
)
async def update_requirement_analysis(
    requirement_analysis_id: UUID,
    data: RequirementAnalysisUpdate,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """更新需求分析"""
    service = RequirementAnalysisService(db)
    current_user = await _get_current_user(service, current_user_id)
    result = await service.update_requirement_analysis(
        requirement_analysis_id=requirement_analysis_id,
        data=data,
        current_user=current_user
    )
    return Response(data=result, message="需求分析更新成功")


@router.delete(
    "/{requirement_analysis_id}",
    response_model=SuccessResponse,
    summary="删除需求分析",
    description="删除指定的需求分析"
)
async def delete_requirement_analysis(
    requirement_analysis_id: UUID,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """删除需求分析"""
    service = RequirementAnalysisService(db)
    current_user = await _get_current_user(service, current_user_id)
    await service.delete_requirement_analysis(
        requirement_analysis_id=requirement_analysis_id,
        current_user=current_user
    )
    return SuccessResponse(message="需求分析删除成功")


@router.get(
    "",
    response_model=PaginatedResponse[RequirementAnalysisMinifiedInfo],
    summary="获取需求分析列表",
    description="获取需求分析列表，支持分页和筛选"
)
async def list_requirement_analyses(
    current_user_id: CurrentUserIdDep,
    project_id: Optional[UUID] = Query(None, description="项目 ID"),
    status: Optional[RequirementAnalysisStatus] = Query(None, description="分析状态"),
    owner_id: Optional[UUID] = Query(None, description="负责人 ID"),
    created_by: Optional[UUID] = Query(None, description="创建者 ID"),
    tags: Optional[List[str]] = Query(None, description="标签列表"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    order_by: str = Query("created_at", description="排序字段"),
    order_direction: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    db: AsyncSession = Depends(get_db),
):
    """获取需求分析列表"""
    service = RequirementAnalysisService(db)
    items, total = await service.list_requirement_analyses(
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
    return PaginatedResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get(
    "/projects/{project_id}/requirement-analyses",
    response_model=Response[List[RequirementAnalysisMinifiedInfo]],
    summary="获取项目的需求分析列表",
    description="获取指定项目的所有需求分析"
)
async def get_project_requirement_analyses(
    project_id: UUID,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """获取项目的需求分析列表"""
    service = RequirementAnalysisService(db)
    result = await service.get_project_requirement_analyses(project_id)
    return Response(data=result)


@router.get(
    "/projects/{project_id}/statistics",
    response_model=Response[dict],
    summary="获取需求分析统计信息",
    description="获取项目的需求分析统计数据"
)
async def get_requirement_analysis_statistics(
    project_id: UUID,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """获取需求分析统计信息"""
    service = RequirementAnalysisService(db)
    result = await service.get_statistics(project_id)
    return Response(data=result)


@router.patch(
    "/{requirement_analysis_id}/status",
    response_model=Response[RequirementAnalysisInfo],
    summary="更新需求分析状态",
    description="更新需求分析的状态"
)
async def update_requirement_analysis_status(
    requirement_analysis_id: UUID,
    status: RequirementAnalysisStatus,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """更新需求分析状态"""
    service = RequirementAnalysisService(db)
    current_user = await _get_current_user(service, current_user_id)
    result = await service.update_status(
        requirement_analysis_id=requirement_analysis_id,
        status=status,
        current_user=current_user
    )
    return Response(data=result, message="状态更新成功")


@router.patch(
    "/bulk/status",
    response_model=SuccessResponse,
    summary="批量更新需求分析状态",
    description="批量更新多个需求分析的状态"
)
async def bulk_update_requirement_analysis_status(
    requirement_analysis_ids: List[UUID],
    status: RequirementAnalysisStatus,
    current_user_id: CurrentUserIdDep,
    db: AsyncSession = Depends(get_db),
):
    """批量更新需求分析状态"""
    service = RequirementAnalysisService(db)
    current_user = await _get_current_user(service, current_user_id)
    count = await service.bulk_update_status(
        requirement_analysis_ids=requirement_analysis_ids,
        status=status,
        current_user=current_user
    )
    return SuccessResponse(message=f"成功更新 {count} 个需求分析的状态")


@router.get(
    "/projects/{project_id}/search-by-tags",
    response_model=Response[List[RequirementAnalysisMinifiedInfo]],
    summary="根据标签搜索需求分析",
    description="根据标签搜索需求分析"
)
async def search_requirement_analyses_by_tags(
    project_id: UUID,
    current_user_id: CurrentUserIdDep,
    tags: List[str] = Query(..., description="标签列表"),
    match_all: bool = Query(False, description="是否必须匹配所有标签"),
    db: AsyncSession = Depends(get_db),
):
    """根据标签搜索需求分析"""
    service = RequirementAnalysisService(db)
    result = await service.search_by_tags(
        project_id=project_id,
        tags=tags,
        match_all=match_all
    )
    return Response(data=result)


@router.get(
    "/{requirement_analysis_id}/download",
    response_model=RequirementAnalysisDownloadResponse,
    summary="下载需求分析报告",
    description="生成并下载需求分析报告"
)
async def download_requirement_analysis_report(
    requirement_analysis_id: UUID,
    current_user_id: CurrentUserIdDep,
    format: str = Query("pdf", regex="^(pdf|word|markdown)$", description="报告格式"),
    db: AsyncSession = Depends(get_db),
):
    """下载需求分析报告"""
    service = RequirementAnalysisService(db)
    result = await service.generate_download_url(
        requirement_analysis_id=requirement_analysis_id,
        format=format
    )
    return result


@router.post(
    "/{requirement_analysis_id}/analyze",
    response_model=Response[dict],
    summary="触发 AI 智能分析",
    description="触发 AI 对需求文档进行智能分析"
)
async def trigger_ai_analysis(
    requirement_analysis_id: UUID,
    current_user_id: CurrentUserIdDep,
    document_content: Optional[str] = None,
    use_rag: bool = Query(False, description="是否使用 RAG 检索"),
    rag_query: Optional[str] = Query(None, description="RAG 检索查询"),
    db: AsyncSession = Depends(get_db),
):
    """触发 AI 智能分析"""
    service = RequirementAnalysisService(db)
    result = await service.trigger_ai_analysis(
        requirement_analysis_id=requirement_analysis_id,
        document_content=document_content,
        use_rag=use_rag,
        rag_query=rag_query
    )
    return Response(data=result, message="AI 分析任务已启动")

