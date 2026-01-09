"""
需求分析控制器
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.service.requirement_analysis_service import RequirementAnalysisService
from module_testing.service.ai_service import AIGenerationService
from module_testing.entity.vo.requirement_analysis_vo import (
    RequirementAnalysisVO, RequirementAnalysisQueryVO, RequirementAnalysisGenerateVO
)
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/requirement", tags=["需求分析管理"])
requirement_service = RequirementAnalysisService()
ai_service = AIGenerationService()


@router.post("/create", summary="创建需求分析")
async def create_requirement(
    requirement_vo: RequirementAnalysisVO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """创建需求分析"""
    try:
        result = await requirement_service.create_requirement(
            db, requirement_vo, current_user.user.user_id if current_user.user else None
        )
        
        # 保存到MinIO
        minio_url = await requirement_service.save_to_minio(result, 'json')
        
        return ResponseUtil.success(data={
            'requirement_id': result.requirement_id,
            'requirement_identifier': result.requirement_identifier,
            'minio_url': minio_url
        }, msg="创建需求分析成功")
        
    except Exception as e:
        logger.error(f"创建需求分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"创建需求分析失败: {str(e)}")


@router.put("/update/{requirement_id}", summary="更新需求分析")
async def update_requirement(
    requirement_id: int = Path(..., description="需求ID"),
    requirement_vo: RequirementAnalysisVO = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """更新需求分析"""
    try:
        result = await requirement_service.update_requirement(
            db, requirement_id, requirement_vo, current_user.user.user_id if current_user.user else None
        )
        
        # 更新MinIO中的文件
        minio_url = await requirement_service.save_to_minio(result, 'json')
        
        return ResponseUtil.success(data={
            'requirement_id': result.requirement_id,
            'minio_url': minio_url
        }, msg="更新需求分析成功")
        
    except Exception as e:
        logger.error(f"更新需求分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"更新需求分析失败: {str(e)}")


@router.delete("/delete/{requirement_id}", summary="删除需求分析")
async def delete_requirement(
    requirement_id: int = Path(..., description="需求ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """删除需求分析"""
    try:
        result = await requirement_service.delete_requirement(db, requirement_id)
        if result:
            return ResponseUtil.success(msg="删除需求分析成功")
        else:
            return ResponseUtil.failure(msg="需求分析不存在")
    except Exception as e:
        logger.error(f"删除需求分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"删除需求分析失败: {str(e)}")


@router.get("/detail/{requirement_id}", summary="获取需求分析详情")
async def get_requirement(
    requirement_id: int = Path(..., description="需求ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """获取需求分析详情"""
    try:
        result = await requirement_service.get_requirement(db, requirement_id)
        if result:
            return ResponseUtil.success(data=result.to_dict() if hasattr(result, "to_dict") else result)
        else:
            return ResponseUtil.failure(msg="需求分析不存在")
    except Exception as e:
        logger.error(f"获取需求分析详情失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取需求分析详情失败: {str(e)}")


@router.get("/list", summary="查询需求分析列表")
async def query_requirement_list(
    project_id: Optional[int] = Query(None, description="项目ID"),
    requirement_name: Optional[str] = Query(None, description="需求名称"),
    requirement_type: Optional[str] = Query(None, description="需求类型"),
    priority: Optional[str] = Query(None, description="优先级"),
    status: Optional[str] = Query(None, description="状态"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """查询需求分析列表"""
    try:
        query_vo = RequirementAnalysisQueryVO(
            project_id=project_id,
            requirement_name=requirement_name,
            requirement_type=requirement_type,
            priority=priority,
            status=status,
            page_num=page_num,
            page_size=page_size
        )
        
        records, total = await requirement_service.query_requirement_list(db, query_vo)
        
        return ResponseUtil.success(data={
            'records': [record.to_dict() if hasattr(record, "to_dict") else record for record in records],
            'total': total,
            'page_num': page_num,
            'page_size': page_size
        })
        
    except Exception as e:
        logger.error(f"查询需求分析列表失败: {str(e)}")
        return ResponseUtil.failure(msg=f"查询需求分析列表失败: {str(e)}")


@router.post("/ai-generate", summary="AI生成需求分析")
async def ai_generate_requirement(
    generate_vo: RequirementAnalysisGenerateVO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """AI生成需求分析"""
    try:
        # 调用AI生成服务
        ai_result = await ai_service.generate(
            generation_type='requirement',
            input_data=generate_vo.dict(),
            thread_id=generate_vo.thread_id
        )
        
        if not ai_result['success']:
            return ResponseUtil.failure(msg=f"AI生成失败: {ai_result.get('error')}")
        
        # 如果需要自动保存
        if generate_vo.auto_save:
            generated_data = ai_result['data']
            requirement_vo = RequirementAnalysisVO(
                project_id=generate_vo.project_id,
                requirement_name=generated_data.get('requirement_name'),
                requirement_type=generated_data.get('requirement_type'),
                priority=generated_data.get('priority'),
                module=generated_data.get('module'),
                description=generated_data.get('description'),
                acceptance_criteria=generated_data.get('acceptance_criteria'),
                functional_requirements=generated_data.get('functional_requirements'),
                non_functional_requirements=generated_data.get('non_functional_requirements'),
                business_rules=generated_data.get('business_rules'),
                dependencies=generated_data.get('dependencies'),
                stakeholders=generated_data.get('stakeholders')
            )
            
            result = await requirement_service.create_requirement(
                db, requirement_vo, current_user.user.user_id if current_user.user else None
            )
            
            # 保存到MinIO
            minio_url = await requirement_service.save_to_minio(result, 'json')
            
            return ResponseUtil.success(data={
                'requirement_id': result.requirement_id,
                'requirement_identifier': result.requirement_identifier,
                'generated_data': generated_data,
                'minio_url': minio_url,
                'messages': ai_result.get('messages', [])
            }, msg="AI生成并保存需求分析成功")
        else:
            return ResponseUtil.success(data={
                'generated_data': ai_result['data'],
                'messages': ai_result.get('messages', [])
            }, msg="AI生成需求分析成功")
        
    except Exception as e:
        logger.error(f"AI生成需求分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI生成需求分析失败: {str(e)}")


@router.get("/download/{requirement_id}", summary="下载需求分析")
async def download_requirement(
    requirement_id: int = Path(..., description="需求ID"),
    format: str = Query('json', description="文件格式 json/markdown"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """下载需求分析"""
    try:
        requirement = await requirement_service.get_requirement(db, requirement_id)
        if not requirement:
            return ResponseUtil.failure(msg="需求分析不存在")
        
        # 生成下载URL
        minio_url = await requirement_service.save_to_minio(requirement, format)
        
        return ResponseUtil.success(data={
            'download_url': minio_url,
            'file_name': f"requirement_{requirement.requirement_identifier}.{format}"
        }, msg="生成下载链接成功")
        
    except Exception as e:
        logger.error(f"下载需求分析失败: {str(e)}")
        return ResponseUtil.failure(msg=f"下载需求分析失败: {str(e)}")
