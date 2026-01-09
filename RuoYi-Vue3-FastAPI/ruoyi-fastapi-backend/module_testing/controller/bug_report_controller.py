"""
缺陷报告控制器
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.service.bug_report_service import BugReportService
from module_testing.service.ai_service import AIGenerationService
from module_testing.entity.vo.bug_report_vo import BugReportVO, BugReportQueryVO, BugReportGenerateVO
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/bug-report", tags=["缺陷报告管理"])
bug_report_service = BugReportService()
ai_service = AIGenerationService()


@router.post("/create", summary="创建缺陷报告")
async def create_bug_report(
    bug_report_vo: BugReportVO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """创建缺陷报告"""
    try:
        result = await bug_report_service.create_bug_report(
            db, bug_report_vo, current_user.user.user_id if current_user.user else None
        )
        
        # 保存到MinIO
        minio_url = await bug_report_service.save_to_minio(result, 'json')
        
        return ResponseUtil.success(data={
            'bug_id': result.bug_id,
            'bug_identifier': result.bug_identifier,
            'minio_url': minio_url
        }, msg="创建缺陷报告成功")
        
    except Exception as e:
        logger.error(f"创建缺陷报告失败: {str(e)}")
        return ResponseUtil.failure(msg=f"创建缺陷报告失败: {str(e)}")


@router.put("/update/{bug_id}", summary="更新缺陷报告")
async def update_bug_report(
    bug_id: int = Path(..., description="缺陷报告ID"),
    bug_report_vo: BugReportVO = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """更新缺陷报告"""
    try:
        result = await bug_report_service.update_bug_report(
            db, bug_id, bug_report_vo, current_user.user.user_id if current_user.user else None
        )
        
        # 更新MinIO中的文件
        minio_url = await bug_report_service.save_to_minio(result, 'json')
        
        return ResponseUtil.success(data={
            'bug_id': result.bug_id,
            'minio_url': minio_url
        }, msg="更新缺陷报告成功")
        
    except Exception as e:
        logger.error(f"更新缺陷报告失败: {str(e)}")
        return ResponseUtil.failure(msg=f"更新缺陷报告失败: {str(e)}")


@router.delete("/delete/{bug_id}", summary="删除缺陷报告")
async def delete_bug_report(
    bug_id: int = Path(..., description="缺陷报告ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """删除缺陷报告"""
    try:
        result = await bug_report_service.delete_bug_report(db, bug_id)
        if result:
            return ResponseUtil.success(msg="删除缺陷报告成功")
        else:
            return ResponseUtil.failure(msg="缺陷报告不存在")
    except Exception as e:
        logger.error(f"删除缺陷报告失败: {str(e)}")
        return ResponseUtil.failure(msg=f"删除缺陷报告失败: {str(e)}")


@router.get("/detail/{bug_id}", summary="获取缺陷报告详情")
async def get_bug_report(
    bug_id: int = Path(..., description="缺陷报告ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """获取缺陷报告详情"""
    try:
        result = await bug_report_service.get_bug_report(db, bug_id)
        if result:
            return ResponseUtil.success(data=result.to_dict() if hasattr(result, "to_dict") else result)
        else:
            return ResponseUtil.failure(msg="缺陷报告不存在")
    except Exception as e:
        logger.error(f"获取缺陷报告详情失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取缺陷报告详情失败: {str(e)}")


@router.get("/list", summary="查询缺陷报告列表")
async def query_bug_report_list(
    project_id: Optional[int] = Query(None, description="项目ID"),
    bug_title: Optional[str] = Query(None, description="缺陷标题"),
    severity: Optional[str] = Query(None, description="严重程度"),
    priority: Optional[str] = Query(None, description="优先级"),
    status: Optional[str] = Query(None, description="状态"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """查询缺陷报告列表"""
    try:
        query_vo = BugReportQueryVO(
            project_id=project_id,
            bug_title=bug_title,
            severity=severity,
            priority=priority,
            status=status,
            page_num=page_num,
            page_size=page_size
        )
        
        records, total = await bug_report_service.query_bug_report_list(db, query_vo)
        
        return ResponseUtil.success(data={
            'records': [record.to_dict() if hasattr(record, "to_dict") else record for record in records],
            'total': total,
            'page_num': page_num,
            'page_size': page_size
        })
        
    except Exception as e:
        logger.error(f"查询缺陷报告列表失败: {str(e)}")
        return ResponseUtil.failure(msg=f"查询缺陷报告列表失败: {str(e)}")


@router.post("/ai-generate", summary="AI生成缺陷报告")
async def ai_generate_bug_report(
    generate_vo: BugReportGenerateVO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """AI生成缺陷报告"""
    try:
        # 调用AI生成服务
        ai_result = await ai_service.generate(
            generation_type='bug_report',
            input_data=generate_vo.dict(),
            thread_id=generate_vo.thread_id
        )
        
        if not ai_result['success']:
            return ResponseUtil.failure(msg=f"AI生成失败: {ai_result.get('error')}")
        
        # 如果需要自动保存
        if generate_vo.auto_save:
            generated_data = ai_result['data']
            bug_report_vo = BugReportVO(
                project_id=generate_vo.project_id,
                bug_title=generated_data.get('bug_title'),
                bug_description=generated_data.get('bug_description'),
                severity=generated_data.get('severity'),
                priority=generated_data.get('priority'),
                bug_type=generated_data.get('bug_type'),
                environment=generated_data.get('environment'),
                steps_to_reproduce=generated_data.get('steps_to_reproduce'),
                expected_behavior=generated_data.get('expected_behavior'),
                actual_behavior=generated_data.get('actual_behavior')
            )
            
            result = await bug_report_service.create_bug_report(
                db, bug_report_vo, current_user.user.user_id if current_user.user else None
            )
            
            # 保存到MinIO
            minio_url = await bug_report_service.save_to_minio(result, 'json')
            
            return ResponseUtil.success(data={
                'bug_id': result.bug_id,
                'bug_identifier': result.bug_identifier,
                'generated_data': generated_data,
                'minio_url': minio_url,
                'messages': ai_result.get('messages', [])
            }, msg="AI生成并保存缺陷报告成功")
        else:
            return ResponseUtil.success(data={
                'generated_data': ai_result['data'],
                'messages': ai_result.get('messages', [])
            }, msg="AI生成缺陷报告成功")
        
    except Exception as e:
        logger.error(f"AI生成缺陷报告失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI生成缺陷报告失败: {str(e)}")


@router.get("/download/{bug_id}", summary="下载缺陷报告")
async def download_bug_report(
    bug_id: int = Path(..., description="缺陷报告ID"),
    format: str = Query('json', description="文件格式 json/markdown"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """下载缺陷报告"""
    try:
        bug_report = await bug_report_service.get_bug_report(db, bug_id)
        if not bug_report:
            return ResponseUtil.failure(msg="缺陷报告不存在")
        
        # 生成下载URL
        minio_url = await bug_report_service.save_to_minio(bug_report, format)
        
        return ResponseUtil.success(data={
            'download_url': minio_url,
            'file_name': f"bug_report_{bug_report.bug_identifier}.{format}"
        }, msg="生成下载链接成功")
        
    except Exception as e:
        logger.error(f"下载缺陷报告失败: {str(e)}")
        return ResponseUtil.failure(msg=f"下载缺陷报告失败: {str(e)}")
