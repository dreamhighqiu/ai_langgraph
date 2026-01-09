"""
缺陷分析控制器
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from module_testing.service.defect_analysis_service import DefectAnalysisService
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/defect-analysis", tags=["缺陷分析管理"])
defect_service = DefectAnalysisService()


# ================ 请求模型 ================

class DefectAnalysisCreate(BaseModel):
    """创建缺陷分析"""
    project_id: int
    knowledge_id: Optional[int] = None
    defect_id: Optional[str] = None
    analysis_name: str
    defect_title: str
    defect_description: str
    severity: str = "medium"
    priority: str = "medium"
    defect_type: Optional[str] = None
    category: Optional[str] = None
    affected_phase: Optional[str] = None
    detection_phase: Optional[str] = None
    executive_summary: Optional[str] = None
    root_cause_analysis: Optional[dict] = None
    impact_analysis: Optional[dict] = None
    reproduction_steps: Optional[list] = None
    affected_modules: Optional[list] = None
    fix_suggestions: Optional[list] = None
    test_suggestions: Optional[list] = None
    prevention_measures: Optional[list] = None
    similar_defects: Optional[list] = None
    use_rag: int = 0
    rag_context: Optional[str] = None
    mindmap_data: Optional[dict] = None
    mindmap_url: Optional[str] = None
    status: str = "draft"
    process_status: Optional[str] = None
    tags: Optional[list] = None
    remark: Optional[str] = None


class DefectAnalysisUpdate(BaseModel):
    """更新缺陷分析"""
    analysis_name: Optional[str] = None
    defect_title: Optional[str] = None
    defect_description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    defect_type: Optional[str] = None
    category: Optional[str] = None
    executive_summary: Optional[str] = None
    root_cause_analysis: Optional[dict] = None
    impact_analysis: Optional[dict] = None
    reproduction_steps: Optional[list] = None
    affected_modules: Optional[list] = None
    fix_suggestions: Optional[list] = None
    test_suggestions: Optional[list] = None
    prevention_measures: Optional[list] = None
    status: Optional[str] = None
    tags: Optional[list] = None
    remark: Optional[str] = None


# ================ 端点 ================

@router.post("/create", summary="创建缺陷分析")
async def create_defect_analysis(
    request: DefectAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """创建缺陷分析"""
    try:
        result = await defect_service.create_analysis(
            db, request.dict(), current_user['user_id']
        )
        
        return ResponseUtil.success(data={
            'analysis_id': result.analysis_id,
            'analysis_name': result.analysis_name
        }, msg="创建缺陷分析成功")
        
    except Exception as e:
        logger.error(f"创建缺陷分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"创建缺陷分析失败: {str(e)}")


@router.put("/update/{analysis_id}", summary="更新缺陷分析")
async def update_defect_analysis(
    analysis_id: int = Path(..., description="分析ID"),
    request: DefectAnalysisUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """更新缺陷分析"""
    try:
        result = await defect_service.update_analysis(
            db, analysis_id, request.dict(exclude_unset=True), current_user['user_id']
        )
        
        if result:
            return ResponseUtil.success(data={
                'analysis_id': result.analysis_id
            }, msg="更新缺陷分析成功")
        else:
            return error(msg="缺陷分析不存在")
        
    except Exception as e:
        logger.error(f"更新缺陷分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"更新缺陷分析失败: {str(e)}")


@router.delete("/delete/{analysis_id}", summary="删除缺陷分析")
async def delete_defect_analysis(
    analysis_id: int = Path(..., description="分析ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """删除缺陷分析"""
    try:
        result = await defect_service.delete_analysis(db, analysis_id)
        if result:
            return success(msg="删除缺陷分析成功")
        else:
            return error(msg="缺陷分析不存在")
    except Exception as e:
        logger.error(f"删除缺陷分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"删除缺陷分析失败: {str(e)}")


@router.get("/detail/{analysis_id}", summary="获取缺陷分析详情")
async def get_defect_analysis(
    analysis_id: int = Path(..., description="分析ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """获取缺陷分析详情"""
    try:
        result = await defect_service.get_analysis(db, analysis_id)
        if result:
            return success(data=result)
        else:
            return error(msg="缺陷分析不存在")
    except Exception as e:
        logger.error(f"获取缺陷分析详情失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取缺陷分析详情失败: {str(e)}")


@router.get("/list", summary="查询缺陷分析列表")
async def query_defect_analysis_list(
    project_id: Optional[int] = Query(None, description="项目ID"),
    analysis_name: Optional[str] = Query(None, description="分析名称"),
    severity: Optional[str] = Query(None, description="严重程度"),
    priority: Optional[str] = Query(None, description="优先级"),
    status: Optional[str] = Query(None, description="状态"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """查询缺陷分析列表"""
    try:
        query_params = {
            'project_id': project_id,
            'analysis_name': analysis_name,
            'severity': severity,
            'priority': priority,
            'status': status,
            'page_num': page_num,
            'page_size': page_size
        }

        records, total = await defect_service.query_analysis_list(db, query_params)

        return ResponseUtil.success(data={
            'records': records,
            'total': total,
            'page_num': page_num,
            'page_size': page_size
        })

    except Exception as e:
        logger.error(f"查询缺陷分析列表失败: {str(e)}")
        return ResponseUtil.failure(msg=f"查询缺陷分析列表失败: {str(e)}")

