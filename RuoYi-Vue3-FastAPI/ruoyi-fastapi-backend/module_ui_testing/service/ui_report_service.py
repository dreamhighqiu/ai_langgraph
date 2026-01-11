"""
UI自动化测试报告服务 - 业务逻辑层
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_ui_testing.dao.ui_report_dao import UIReportDAO
from module_ui_testing.entity.do.ui_report_do import UITestReport
from module_ui_testing.entity.vo.ui_report_vo import (
    UIReportDetailModel,
    UIReportModel,
    UIReportPageQueryModel,
)
from utils.log_util import logger


class UIReportService:
    """UI自动化测试报告服务"""
    
    @staticmethod
    async def get_report_list(
        db: AsyncSession,
        query: UIReportPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取报告列表"""
        reports, total = await UIReportDAO.get_list(db, query, is_page)
        
        rows = [UIReportModel.model_validate(r) for r in reports]
        
        return {
            'rows': rows,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_report_detail(db: AsyncSession, report_id: int) -> UIReportDetailModel | None:
        """获取报告详情"""
        result = await UIReportDAO.get_detail(db, report_id)
        if result:
            return UIReportDetailModel.model_validate(result)
        return None
    
    @staticmethod
    async def create_report(
        db: AsyncSession,
        execution_id: int,
        report_name: str,
        report_type: str,
        report_path: str = None,
        report_size: int = None,
        summary: dict = None,
        metrics: dict = None
    ) -> dict[str, Any]:
        """创建报告"""
        try:
            report = UITestReport(
                execution_id=execution_id,
                report_name=report_name,
                report_type=report_type,
                report_path=report_path,
                report_size=report_size,
                summary=summary,
                metrics=metrics
            )
            
            created = await UIReportDAO.create(db, report)
            report_id = created.report_id
            await db.commit()
            
            logger.info(f'创建UI自动化测试报告成功: {report_id}')
            
            return {
                'success': True,
                'report_id': report_id
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'创建UI自动化测试报告失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def delete_report(db: AsyncSession, report_id: int) -> bool:
        """删除报告"""
        try:
            success = await UIReportDAO.delete_by_id(db, report_id)
            await db.commit()
            return success
        except Exception as e:
            await db.rollback()
            logger.error(f'删除报告失败: {e}')
            return False
    
    @staticmethod
    async def get_reports_by_execution(db: AsyncSession, execution_id: int) -> list[UIReportModel]:
        """获取执行记录的报告列表"""
        reports = await UIReportDAO.get_by_execution(db, execution_id)
        return [UIReportModel.model_validate(r) for r in reports]
    
    @staticmethod
    async def compare_reports(db: AsyncSession, report_ids: list[int]) -> dict[str, Any]:
        """对比报告"""
        reports = await UIReportDAO.get_by_ids(db, report_ids)
        
        if len(reports) < 2:
            return {
                'success': False,
                'error': '至少需要2个报告进行对比'
            }
        
        # 简单的对比逻辑
        comparison = {
            'report_count': len(reports),
            'reports': reports,
            'metrics_comparison': {}
        }
        
        return {
            'success': True,
            'comparison': comparison
        }

