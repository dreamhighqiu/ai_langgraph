"""
测试执行记录DAO - 数据访问层
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.execution_do import TestExecution
from module_testing.entity.do.project_do import TestProject
from module_testing.entity.do.script_do import TestScript
from module_testing.entity.vo.execution_vo import ExecutionPageQueryModel


class ExecutionDAO:
    """测试执行记录数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, execution_id: int) -> Optional[TestExecution]:
        """根据ID获取执行记录"""
        result = await db.execute(
            select(TestExecution).where(TestExecution.execution_id == execution_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_detail(db: AsyncSession, execution_id: int) -> Optional[dict]:
        """获取执行详情(包含脚本和项目信息)"""
        result = await db.execute(
            select(
                TestExecution,
                TestScript.script_name,
                TestScript.script_type,
                TestScript.script_content,
                TestScript.script_file_path,
                TestProject.project_name,
                TestProject.project_id
            )
            .join(TestScript, TestExecution.script_id == TestScript.script_id)
            .join(TestProject, TestScript.project_id == TestProject.project_id)
            .where(TestExecution.execution_id == execution_id)
        )
        row = result.first()
        if row:
            execution, script_name, script_type, script_content, script_file_path, project_name, project_id = row
            return {
                'execution_id': execution.execution_id,
                'script_id': execution.script_id,
                'project_id': project_id,
                'script_name': script_name,
                'script_type': script_type,
                'script_content': script_content,
                'script_file_path': script_file_path,
                'project_name': project_name,
                'execution_type': execution.execution_type,
                'execution_status': execution.execution_status,
                'start_time': execution.start_time,
                'end_time': execution.end_time,
                'duration': execution.duration,
                'thread_id': execution.thread_id,
                'agent_id': execution.agent_id,
                'config': execution.config,
                'result': execution.result,
                'error_msg': execution.error_msg,
                'executor': execution.executor,
                'create_time': execution.create_time,
            }
        return None
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: ExecutionPageQueryModel,
        is_page: bool = True
    ) -> tuple[list[dict], int]:
        """获取执行记录列表"""
        # 构建查询条件
        conditions = []
        
        if query.script_id:
            conditions.append(TestExecution.script_id == query.script_id)
        if query.execution_status:
            conditions.append(TestExecution.execution_status == query.execution_status)
        if query.execution_type:
            conditions.append(TestExecution.execution_type == query.execution_type)
        if query.executor:
            conditions.append(TestExecution.executor.like(f'%{query.executor}%'))
        if query.begin_time:
            conditions.append(TestExecution.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(TestExecution.create_time <= query.end_time)
        
        # 查询总数
        count_query = select(func.count(TestExecution.execution_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        list_query = (
            select(
                TestExecution,
                TestScript.script_name,
                TestScript.script_type,
                TestProject.project_name,
                TestProject.project_id,
                TestScript.script_file_path
            )
            .join(TestScript, TestExecution.script_id == TestScript.script_id)
            .join(TestProject, TestScript.project_id == TestProject.project_id)
        )
        
        if conditions:
            list_query = list_query.where(and_(*conditions))
        
        list_query = list_query.order_by(TestExecution.create_time.desc())
        
        if is_page:
            offset = (query.page_num - 1) * query.page_size
            list_query = list_query.offset(offset).limit(query.page_size)
        
        result = await db.execute(list_query)
        rows = result.all()
        
        executions = []
        for execution, script_name, script_type, project_name, project_id, script_file_path in rows:
            exec_dict = {
                'execution_id': execution.execution_id,
                'script_id': execution.script_id,
                'project_id': project_id,
                'script_name': script_name,
                'script_type': script_type,
                'project_name': project_name,
                'script_file_path': script_file_path,
                'execution_type': execution.execution_type,
                'execution_status': execution.execution_status,
                'start_time': execution.start_time,
                'end_time': execution.end_time,
                'duration': execution.duration,
                'thread_id': execution.thread_id,
                'agent_id': execution.agent_id,
                'result': execution.result,
                'error_msg': execution.error_msg,
                'executor': execution.executor,
                'create_time': execution.create_time,
            }
            executions.append(exec_dict)
        
        return executions, total
    
    @staticmethod
    async def create(db: AsyncSession, execution: TestExecution) -> TestExecution:
        """创建执行记录"""
        db.add(execution)
        await db.flush()
        await db.refresh(execution)
        return execution
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        execution_id: int,
        status: str,
        **kwargs
    ) -> bool:
        """更新执行状态"""
        values = {'execution_status': status, **kwargs}
        result = await db.execute(
            update(TestExecution)
            .where(TestExecution.execution_id == execution_id)
            .values(**values)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def update_result(
        db: AsyncSession,
        execution_id: int,
        result_data: dict,
        status: str = 'success',
        end_time: datetime = None
    ) -> bool:
        """更新执行结果"""
        values = {
            'execution_status': status,
            'result': result_data,
            'end_time': end_time or datetime.now()
        }
        if end_time:
            # 计算执行时长
            execution = await ExecutionDAO.get_by_id(db, execution_id)
            if execution and execution.start_time:
                duration = int((end_time - execution.start_time).total_seconds())
                values['duration'] = duration
        
        result = await db.execute(
            update(TestExecution)
            .where(TestExecution.execution_id == execution_id)
            .values(**values)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def get_running_executions(db: AsyncSession) -> list[TestExecution]:
        """获取正在运行的执行记录"""
        result = await db.execute(
            select(TestExecution).where(
                TestExecution.execution_status == 'running'
            )
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def count_by_script(db: AsyncSession, script_id: int) -> int:
        """统计脚本的执行次数"""
        result = await db.execute(
            select(func.count(TestExecution.execution_id)).where(
                TestExecution.script_id == script_id
            )
        )
        return result.scalar() or 0
    
    @staticmethod
    async def get_statistics(db: AsyncSession, days: int = 7) -> dict:
        """获取执行统计数据"""
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        # 总执行数
        total_result = await db.execute(
            select(func.count(TestExecution.execution_id)).where(
                TestExecution.create_time >= start_date
            )
        )
        total = total_result.scalar() or 0
        
        # 成功数
        success_result = await db.execute(
            select(func.count(TestExecution.execution_id)).where(
                and_(
                    TestExecution.create_time >= start_date,
                    TestExecution.execution_status == 'success'
                )
            )
        )
        success = success_result.scalar() or 0
        
        # 失败数
        failed_result = await db.execute(
            select(func.count(TestExecution.execution_id)).where(
                and_(
                    TestExecution.create_time >= start_date,
                    TestExecution.execution_status == 'failed'
                )
            )
        )
        failed = failed_result.scalar() or 0
        
        # 运行中
        running_result = await db.execute(
            select(func.count(TestExecution.execution_id)).where(
                TestExecution.execution_status == 'running'
            )
        )
        running = running_result.scalar() or 0
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'running': running,
            'success_rate': round(success / total * 100, 2) if total > 0 else 0
        }

