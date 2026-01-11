"""
UI自动化测试执行服务 - 业务逻辑层
"""
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_ui_testing.dao.ui_execution_dao import UIExecutionDAO
from module_ui_testing.entity.do.ui_execution_do import UITestExecution
from module_ui_testing.entity.vo.ui_execution_vo import (
    UIExecutionDetailModel,
    UIExecutionModel,
    UIExecutionPageQueryModel,
)
from utils.log_util import logger


class UIExecutionService:
    """UI自动化测试执行服务"""
    
    @staticmethod
    async def get_execution_list(
        db: AsyncSession,
        query: UIExecutionPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取执行记录列表"""
        executions, total = await UIExecutionDAO.get_list(db, query, is_page)
        
        rows = [UIExecutionModel.model_validate(e) for e in executions]
        
        return {
            'rows': rows,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_execution_detail(db: AsyncSession, execution_id: int) -> UIExecutionDetailModel | None:
        """获取执行详情"""
        result = await UIExecutionDAO.get_detail(db, execution_id)
        if result:
            return UIExecutionDetailModel.model_validate(result)
        return None
    
    @staticmethod
    async def create_execution(
        db: AsyncSession,
        script_id: int,
        execution_type: str,
        browser: str,
        headless: str,
        executor: str,
        config: dict = None
    ) -> dict[str, Any]:
        """创建执行记录"""
        try:
            execution = UITestExecution(
                script_id=script_id,
                execution_type=execution_type,
                execution_status='pending',
                browser=browser,
                headless=headless,
                config=config,
                executor=executor
            )
            
            created = await UIExecutionDAO.create(db, execution)
            execution_id = created.execution_id
            await db.commit()
            
            logger.info(f'创建UI自动化执行记录成功: {execution_id}')
            
            return {
                'success': True,
                'execution_id': execution_id
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'创建UI自动化执行记录失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def update_execution_status(
        db: AsyncSession,
        execution_id: int,
        status: str,
        **kwargs
    ) -> bool:
        """更新执行状态"""
        try:
            success = await UIExecutionDAO.update_status(db, execution_id, status, **kwargs)
            await db.commit()
            return success
        except Exception as e:
            await db.rollback()
            logger.error(f'更新执行状态失败: {e}')
            return False
    
    @staticmethod
    async def update_execution_result(
        db: AsyncSession,
        execution_id: int,
        result_data: dict,
        status: str = 'success',
        end_time: datetime = None
    ) -> bool:
        """更新执行结果"""
        try:
            success = await UIExecutionDAO.update_result(db, execution_id, result_data, status, end_time)
            await db.commit()
            return success
        except Exception as e:
            await db.rollback()
            logger.error(f'更新执行结果失败: {e}')
            return False
    
    @staticmethod
    async def get_statistics(db: AsyncSession, days: int = 7) -> dict:
        """获取执行统计数据"""
        return await UIExecutionDAO.get_statistics(db, days)

