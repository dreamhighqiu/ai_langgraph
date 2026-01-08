"""
缺陷分析 API 端点

提供缺陷分析的 RESTful API 接口
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSessionDep, CurrentUserIdDep
from app.config.database import get_db
from app.services.defect_analysis_service import DefectAnalysisService
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
from app.schemas.common import SuccessResponse, MessageResponse
from app.schemas.pagination import PaginatedResponse, PaginationInfo

router = APIRouter(prefix="/defect-analysis", tags=["缺陷分析"])


@router.post(
    "/projects/{project_id}/defect-analysis",
    response_model=Response[DefectAnalysisInfo],
    status_code=status.HTTP_201_CREATED,
    summary="创建缺陷分析",
    description="为指定项目创建新的缺陷分析记录"
)
async def create_defect_analysis(
    project_id: UUID,
    data: DefectAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """创建缺陷分析"""
    service = DefectAnalysisService(db)
    result = await service.create_defect_analysis(
        project_id=project_id,
        data=data,
        current_user=current_user
    )
    return Response(data=result, message="缺陷分析创建成功")


@router.get(
    "/{defect_analysis_id}",
    response_model=Response[DefectAnalysisInfo],
    summary="获取缺陷分析详情",
    description="根据 ID 获取缺陷分析的详细信息"
)
async def get_defect_analysis(
    defect_analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """获取缺陷分析详情"""
    service = DefectAnalysisService(db)
    result = await service.get_defect_analysis(
        defect_analysis_id=defect_analysis_id,
        current_user=current_user
    )
    return Response(data=result)


@router.put(
    "/{defect_analysis_id}",
    response_model=Response[DefectAnalysisInfo],
    summary="更新缺陷分析",
    description="更新缺陷分析的信息"
)
async def update_defect_analysis(
    defect_analysis_id: UUID,
    data: DefectAnalysisUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """更新缺陷分析"""
    service = DefectAnalysisService(db)
    result = await service.update_defect_analysis(
        defect_analysis_id=defect_analysis_id,
        data=data,
        current_user=current_user
    )
    return Response(data=result, message="缺陷分析更新成功")


@router.delete(
    "/{defect_analysis_id}",
    response_model=SuccessResponse,
    summary="删除缺陷分析",
    description="删除指定的缺陷分析"
)
async def delete_defect_analysis(
    defect_analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """删除缺陷分析"""
    service = DefectAnalysisService(db)
    await service.delete_defect_analysis(
        defect_analysis_id=defect_analysis_id,
        current_user=current_user
    )
    return SuccessResponse(message="缺陷分析删除成功")


@router.get(
    "",
    response_model=PaginatedResponse[DefectAnalysisMinifiedInfo],
    summary="获取缺陷分析列表",
    description="获取缺陷分析列表，支持分页和筛选"
)
async def list_defect_analyses(
    project_id: Optional[UUID] = Query(None, description="项目 ID"),
    status: Optional[DefectAnalysisStatus] = Query(None, description="分析状态"),
    severity: Optional[DefectSeverity] = Query(None, description="严重程度"),
    priority: Optional[DefectPriority] = Query(None, description="优先级"),
    defect_type: Optional[DefectType] = Query(None, description="缺陷类型"),
    owner_id: Optional[UUID] = Query(None, description="负责人 ID"),
    created_by: Optional[UUID] = Query(None, description="创建者 ID"),
    tags: Optional[List[str]] = Query(None, description="标签列表"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    order_by: str = Query("created_at", description="排序字段"),
    order_direction: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """获取缺陷分析列表"""
    service = DefectAnalysisService(db)
    items, total = await service.list_defect_analyses(
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
    return PaginatedResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get(
    "/projects/{project_id}/defect-analyses",
    response_model=Response[List[DefectAnalysisMinifiedInfo]],
    summary="获取项目的缺陷分析列表",
    description="获取指定项目的所有缺陷分析"
)
async def get_project_defect_analyses(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """获取项目的缺陷分析列表"""
    service = DefectAnalysisService(db)
    result = await service.get_project_defect_analyses(project_id)
    return Response(data=result)


@router.get(
    "/projects/{project_id}/statistics",
    response_model=Response[dict],
    summary="获取缺陷分析统计信息",
    description="获取项目的缺陷分析统计数据"
)
async def get_defect_analysis_statistics(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """获取缺陷分析统计信息"""
    service = DefectAnalysisService(db)
    result = await service.get_statistics(project_id)
    return Response(data=result)


@router.patch(
    "/{defect_analysis_id}/status",
    response_model=Response[DefectAnalysisInfo],
    summary="更新缺陷分析状态",
    description="更新缺陷分析的状态"
)
async def update_defect_analysis_status(
    defect_analysis_id: UUID,
    status: DefectAnalysisStatus,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """更新缺陷分析状态"""
    service = DefectAnalysisService(db)
    result = await service.update_status(
        defect_analysis_id=defect_analysis_id,
        status=status,
        current_user=current_user
    )
    return Response(data=result, message="状态更新成功")


@router.patch(
    "/bulk/status",
    response_model=SuccessResponse,
    summary="批量更新缺陷分析状态",
    description="批量更新多个缺陷分析的状态"
)
async def bulk_update_defect_analysis_status(
    defect_analysis_ids: List[UUID],
    status: DefectAnalysisStatus,
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """批量更新缺陷分析状态"""
    service = DefectAnalysisService(db)
    count = await service.bulk_update_status(
        defect_analysis_ids=defect_analysis_ids,
        status=status,
        current_user=current_user
    )
    return SuccessResponse(message=f"成功更新 {count} 个缺陷分析的状态")


@router.get(
    "/projects/{project_id}/search-by-tags",
    response_model=Response[List[DefectAnalysisMinifiedInfo]],
    summary="根据标签搜索缺陷分析",
    description="根据标签搜索缺陷分析"
)
async def search_defect_analyses_by_tags(
    project_id: UUID,
    tags: List[str] = Query(..., description="标签列表"),
    match_all: bool = Query(False, description="是否必须匹配所有标签"),
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """根据标签搜索缺陷分析"""
    service = DefectAnalysisService(db)
    result = await service.search_by_tags(
        project_id=project_id,
        tags=tags,
        match_all=match_all
    )
    return Response(data=result)


@router.get(
    "/projects/{project_id}/high-priority",
    response_model=Response[List[DefectAnalysisMinifiedInfo]],
    summary="获取高优先级缺陷",
    description="获取项目的高优先级缺陷分析"
)
async def get_high_priority_defects(
    project_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """获取高优先级缺陷"""
    service = DefectAnalysisService(db)
    result = await service.get_high_priority_defects(
        project_id=project_id,
        limit=limit
    )
    return Response(data=result)


@router.get(
    "/{defect_analysis_id}/download",
    response_model=DefectAnalysisDownloadResponse,
    summary="下载缺陷分析报告",
    description="生成并下载缺陷分析报告"
)
async def download_defect_analysis_report(
    defect_analysis_id: UUID,
    format: str = Query("pdf", regex="^(pdf|word|markdown)$", description="报告格式"),
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """下载缺陷分析报告"""
    service = DefectAnalysisService(db)
    result = await service.generate_download_url(
        defect_analysis_id=defect_analysis_id,
        format=format
    )
    return result


@router.post(
    "/{defect_analysis_id}/analyze",
    response_model=Response[dict],
    summary="触发 AI 智能分析",
    description="触发 AI 对缺陷报告进行智能分析"
)
async def trigger_ai_analysis(
    defect_analysis_id: UUID,
    document_content: Optional[str] = None,
    use_rag: bool = Query(False, description="是否使用 RAG 检索"),
    rag_query: Optional[str] = Query(None, description="RAG 检索查询"),
    db: AsyncSession = Depends(get_db),
    current_user_id: CurrentUserIdDep
):
    """触发 AI 智能分析"""
    service = DefectAnalysisService(db)
    result = await service.trigger_ai_analysis(
        defect_analysis_id=defect_analysis_id,
        document_content=document_content,
        use_rag=use_rag,
        rag_query=rag_query
    )
    return Response(data=result, message="AI 分析任务已启动")

