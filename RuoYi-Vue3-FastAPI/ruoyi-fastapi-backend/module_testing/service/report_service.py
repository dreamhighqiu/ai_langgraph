"""
测试报告服务 - 业务逻辑层
"""
import json
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.report_dao import ReportDAO
from module_testing.entity.do.report_do import TestReport
from module_testing.entity.vo.report_vo import (
    CompareReportsModel,
    ReportPageQueryModel,
)
from module_testing.storage.minio_client import get_minio_client
from utils.log_util import logger


class ReportService:
    """测试报告服务"""
    
    @staticmethod
    async def get_report_list(
        db: AsyncSession,
        query: ReportPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取报告列表"""
        reports, total = await ReportDAO.get_list(db, query, is_page)
        
        return {
            'rows': reports,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_report_detail(
        db: AsyncSession,
        report_id: int
    ) -> dict | None:
        """获取报告详情"""
        detail = await ReportDAO.get_detail(db, report_id)
        
        if detail and detail.get('report_path'):
            # 从MinIO获取报告内容
            minio_client = get_minio_client()
            success, content = minio_client.download_file(detail['report_path'])
            if success and content:
                try:
                    detail['report_content'] = content.decode('utf-8')
                except:
                    detail['report_content'] = None
        
        return detail
    
    @staticmethod
    async def get_report_download_url(
        db: AsyncSession,
        report_id: int
    ) -> dict[str, Any]:
        """获取报告下载URL"""
        report = await ReportDAO.get_by_id(db, report_id)
        
        if not report:
            return {
                'success': False,
                'error': '报告不存在'
            }
        
        if not report.report_path:
            return {
                'success': False,
                'error': '报告文件不存在'
            }
        
        minio_client = get_minio_client()
        url = minio_client.get_presigned_url(report.report_path)
        
        if url:
            return {
                'success': True,
                'url': url,
                'filename': report.report_name
            }
        
        return {
            'success': False,
            'error': '生成下载链接失败'
        }
    
    @staticmethod
    async def create_report(
        db: AsyncSession,
        execution_id: int,
        report_name: str,
        report_type: str,
        content: str | bytes,
        summary: dict = None,
        metrics: dict = None
    ) -> dict[str, Any]:
        """创建报告"""
        try:
            # 检查执行记录是否存在
            execution = await ExecutionDAO.get_by_id(db, execution_id)
            if not execution:
                return {
                    'success': False,
                    'error': '执行记录不存在'
                }
            
            # 处理内容
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # 保存到MinIO
            minio_client = get_minio_client()
            ext_map = {'html': 'html', 'pdf': 'pdf', 'json': 'json', 'allure': 'zip'}
            ext = ext_map.get(report_type, 'txt')
            object_path = f"reports/{report_type}/{execution_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            
            content_type_map = {
                'html': 'text/html',
                'pdf': 'application/pdf',
                'json': 'application/json',
                'allure': 'application/zip'
            }
            content_type = content_type_map.get(report_type, 'application/octet-stream')
            
            success, path = minio_client.upload_file(
                file_content=content_bytes,
                object_name=object_path,
                content_type=content_type
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f'保存报告文件失败: {path}'
                }
            
            # 创建报告记录
            report = TestReport(
                execution_id=execution_id,
                report_name=report_name,
                report_type=report_type,
                report_path=path,
                report_size=len(content_bytes),
                summary=summary,
                metrics=metrics
            )
            
            created = await ReportDAO.create(db, report)
            await db.commit()
            
            logger.info(f'创建报告成功: {created.report_id}')
            
            return {
                'success': True,
                'report_id': created.report_id,
                'report_path': path
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'创建报告失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def compare_reports(
        db: AsyncSession,
        model: CompareReportsModel
    ) -> dict[str, Any]:
        """报告对比"""
        try:
            reports = await ReportDAO.get_by_ids(db, model.report_ids)
            
            if len(reports) < 2:
                return {
                    'success': False,
                    'error': '至少需要2个报告进行对比'
                }
            
            # 构建对比数据
            comparison = {
                'execution_time': [],
                'status_distribution': {},
                'metrics_comparison': {}
            }
            
            for report in reports:
                # 执行时间对比
                comparison['execution_time'].append({
                    'report_id': report['report_id'],
                    'report_name': report['report_name'],
                    'duration': report.get('duration', 0)
                })
                
                # 指标对比
                if report.get('metrics'):
                    for key, value in report['metrics'].items():
                        if key not in comparison['metrics_comparison']:
                            comparison['metrics_comparison'][key] = []
                        comparison['metrics_comparison'][key].append({
                            'report_id': report['report_id'],
                            'value': value
                        })
            
            return {
                'success': True,
                'reports': reports,
                'comparison': comparison
            }
        
        except Exception as e:
            logger.error(f'报告对比失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def delete_report(
        db: AsyncSession,
        report_id: int
    ) -> dict[str, Any]:
        """删除报告"""
        try:
            report = await ReportDAO.get_by_id(db, report_id)
            
            if not report:
                return {
                    'success': False,
                    'error': '报告不存在'
                }
            
            # 删除MinIO中的文件
            if report.report_path:
                minio_client = get_minio_client()
                minio_client.delete_file(report.report_path)
            
            # 删除数据库记录
            await ReportDAO.delete_by_id(db, report_id)
            await db.commit()
            
            logger.info(f'删除报告成功: {report_id}')
            
            return {'success': True}
        
        except Exception as e:
            await db.rollback()
            logger.error(f'删除报告失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def generate_html_report(
        db: AsyncSession,
        execution_id: int
    ) -> dict[str, Any]:
        """生成HTML报告"""
        try:
            detail = await ExecutionDAO.get_detail(db, execution_id)
            
            if not detail:
                return {
                    'success': False,
                    'error': '执行记录不存在'
                }
            
            # 生成HTML报告内容
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {detail['script_name']}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 2px solid #1890ff; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #1890ff; margin: 0; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .info-item {{ background: #f9f9f9; padding: 15px; border-radius: 6px; }}
        .info-item label {{ color: #666; font-size: 12px; display: block; margin-bottom: 5px; }}
        .info-item value {{ font-size: 16px; font-weight: bold; color: #333; }}
        .status-success {{ color: #52c41a; }}
        .status-failed {{ color: #ff4d4f; }}
        .status-running {{ color: #1890ff; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-left: 4px solid #1890ff; padding-left: 10px; }}
        pre {{ background: #f6f8fa; padding: 15px; border-radius: 6px; overflow-x: auto; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-card .value {{ font-size: 24px; font-weight: bold; }}
        .metric-card .label {{ font-size: 12px; opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 测试报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="info-grid">
            <div class="info-item">
                <label>脚本名称</label>
                <value>{detail['script_name']}</value>
            </div>
            <div class="info-item">
                <label>脚本类型</label>
                <value>{detail['script_type']}</value>
            </div>
            <div class="info-item">
                <label>所属项目</label>
                <value>{detail['project_name']}</value>
            </div>
            <div class="info-item">
                <label>执行状态</label>
                <value class="status-{detail['execution_status']}">{detail['execution_status']}</value>
            </div>
            <div class="info-item">
                <label>执行者</label>
                <value>{detail['executor']}</value>
            </div>
            <div class="info-item">
                <label>执行时长</label>
                <value>{detail.get('duration', 0)}秒</value>
            </div>
        </div>
        
        <div class="section">
            <h2>执行结果</h2>
            <pre>{json.dumps(detail.get('result', {}), indent=2, ensure_ascii=False)}</pre>
        </div>
        
        {f'<div class="section"><h2>错误信息</h2><pre style="color: #ff4d4f;">{detail["error_msg"]}</pre></div>' if detail.get('error_msg') else ''}
        
        <div class="section">
            <h2>测试脚本</h2>
            <pre>{detail.get('script_content', '无脚本内容')}</pre>
        </div>
    </div>
</body>
</html>
"""
            
            # 保存报告
            result = await ReportService.create_report(
                db,
                execution_id=execution_id,
                report_name=f"{detail['script_name']}_报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                report_type='html',
                content=html_content,
                summary={
                    'script_name': detail['script_name'],
                    'status': detail['execution_status'],
                    'duration': detail.get('duration', 0)
                }
            )
            
            return result
        
        except Exception as e:
            logger.error(f'生成HTML报告失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }

