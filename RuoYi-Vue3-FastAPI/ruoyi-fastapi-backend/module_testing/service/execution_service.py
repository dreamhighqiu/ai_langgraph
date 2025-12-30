"""
测试执行服务 - 业务逻辑层
"""
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.report_dao import ReportDAO
from module_testing.entity.vo.execution_vo import (
    CancelExecutionModel,
    ExecutionPageQueryModel,
)
from utils.log_util import logger


class ExecutionService:
    """测试执行服务"""
    
    @staticmethod
    async def get_execution_list(
        db: AsyncSession,
        query: ExecutionPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取执行记录列表"""
        executions, total = await ExecutionDAO.get_list(db, query, is_page)
        
        return {
            'rows': executions,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_execution_detail(
        db: AsyncSession,
        execution_id: int
    ) -> dict | None:
        """获取执行详情"""
        detail = await ExecutionDAO.get_detail(db, execution_id)
        
        if detail:
            # 获取关联的报告
            reports = await ReportDAO.get_by_execution(db, execution_id)
            detail['reports'] = [
                {
                    'report_id': r.report_id,
                    'report_name': r.report_name,
                    'report_type': r.report_type,
                    'create_time': r.create_time
                }
                for r in reports
            ]
        
        return detail
    
    @staticmethod
    async def cancel_execution(
        db: AsyncSession,
        model: CancelExecutionModel
    ) -> dict[str, Any]:
        """取消执行"""
        try:
            execution = await ExecutionDAO.get_by_id(db, model.execution_id)
            
            if not execution:
                return {
                    'success': False,
                    'error': '执行记录不存在'
                }
            
            # 立即提取属性，避免greenlet错误
            exec_status = execution.execution_status
            
            if exec_status not in ['pending', 'running']:
                return {
                    'success': False,
                    'error': f'当前状态[{exec_status}]无法取消'
                }
            
            # 更新状态为已取消
            await ExecutionDAO.update_status(
                db, model.execution_id,
                'cancelled',
                error_msg=model.reason or '用户取消',
                end_time=datetime.now()
            )
            await db.commit()
            
            logger.info(f'取消执行: {model.execution_id}')
            
            return {'success': True}
        
        except Exception as e:
            await db.rollback()
            logger.error(f'取消执行失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def get_execution_status(
        db: AsyncSession,
        execution_id: int
    ) -> dict | None:
        """获取执行状态"""
        execution = await ExecutionDAO.get_by_id(db, execution_id)
        
        if execution:
            # 立即提取所有需要的属性
            return {
                'execution_id': execution.execution_id,
                'execution_status': execution.execution_status,
                'start_time': execution.start_time,
                'end_time': execution.end_time,
                'duration': execution.duration,
                'error_msg': execution.error_msg
            }
        return None
    
    @staticmethod
    async def get_running_executions(db: AsyncSession) -> list[dict]:
        """获取正在运行的执行记录"""
        executions = await ExecutionDAO.get_running_executions(db)
        
        return [
            {
                'execution_id': e.execution_id,
                'script_id': e.script_id,
                'start_time': e.start_time,
                'executor': e.executor
            }
            for e in executions
        ]
    
    @staticmethod
    async def get_statistics(db: AsyncSession, days: int = 7) -> dict[str, Any]:
        """获取执行统计数据"""
        return await ExecutionDAO.get_statistics(db, days)
    
    @staticmethod
    async def retry_execution(
        db: AsyncSession,
        execution_id: int,
        executor: str
    ) -> dict[str, Any]:
        """重试执行"""
        try:
            # 获取原执行记录
            original = await ExecutionDAO.get_by_id(db, execution_id)
            
            if not original:
                return {
                    'success': False,
                    'error': '执行记录不存在'
                }
            
            # 立即提取需要的属性
            orig_status = original.execution_status
            orig_script_id = original.script_id
            orig_config = original.config
            
            if orig_status not in ['failed', 'cancelled']:
                return {
                    'success': False,
                    'error': '只能重试失败或已取消的执行'
                }
            
            # 导入ScriptService避免循环导入
            from module_testing.service.script_service import ScriptService
            from module_testing.entity.vo.script_vo import ExecuteScriptModel
            
            # 使用原配置重新执行
            model = ExecuteScriptModel(
                script_id=orig_script_id,
                config=orig_config,
                execution_type='manual'
            )
            
            result = await ScriptService.execute_script(db, model, executor)
            
            if result['success']:
                logger.info(f'重试执行成功: {execution_id} -> {result["execution_id"]}')
            
            return result
        
        except Exception as e:
            await db.rollback()
            logger.error(f'重试执行失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }

