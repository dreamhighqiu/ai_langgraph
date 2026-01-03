"""
性能测试(K6)专用服务层
"""
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from utils.log_util import logger
from module_testing.agents.agent_manager import get_agent_manager
from module_testing.agents.k6_runner import get_k6_runner
from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.report_dao import ReportDAO
from module_testing.dao.requirement_dao import RequirementDAO
from module_testing.dao.script_dao import ScriptDAO
from module_testing.entity.do.execution_do import TestExecution
from module_testing.entity.do.script_do import TestScript
from module_testing.storage.minio_client import MinIOClient


class PerformanceService:
    """性能测试服务 - 专门处理K6性能测试"""
    
    @staticmethod
    async def generate_k6_script(
        db: AsyncSession,
        user_id: int,
        user_name: str,
        requirement_id: int,
        config: Optional[Dict] = None,
    ) -> Dict:
        """
        AI生成K6性能测试脚本
        
        流程:
        1. 获取需求信息
        2. 调用testing-agents-service的K6 Agent生成脚本
        3. 保存生成的脚本到数据库和MinIO
        4. 返回脚本ID和内容
        """
        requirement = await RequirementDAO.get_by_id(db, requirement_id)
        if not requirement:
            raise ValueError(f'需求不存在: {requirement_id}')
        
        cfg = config or {}
        agent_manager = get_agent_manager()
        requirement_payload = {
            'requirement_id': requirement.requirement_id,
            'requirement_name': requirement.requirement_name,
            'requirement_type': 'performance',
            'description': requirement.description,
            'acceptance_criteria': requirement.acceptance_criteria or '',
        }

        logger.info(f'调用K6 Agent生成脚本, 需求ID: {requirement_id}')
        agent_result = await agent_manager.generate_script(
            agent_id='k6_agent',
            requirement=requirement_payload,
            config=cfg,
        )
        if not agent_result.get('success'):
            raise ValueError(agent_result.get('error', '生成K6脚本失败'))

        script_content = agent_result['script_content']

        # 保存脚本到MinIO
        minio_client = MinIOClient()
        script_filename = f"k6_script_{requirement_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
        script_url = await minio_client.upload_script(
            script_content=script_content,
            filename=script_filename,
        )

        # 保存脚本元数据到数据库
        script = TestScript(
            script_name=f"{requirement.requirement_name}_性能测试脚本",
            script_type='k6',
            project_id=requirement.project_id,
            requirement_id=requirement_id,
            script_content=script_content,
            script_url=script_url,
            config=json.dumps(cfg),
            status='0',  # 未执行
            agent_id='k6_agent',
            generation_prompt=requirement.description,
            create_by=user_name,
        )

        db.add(script)
        await db.flush()
        await db.refresh(script)
        await db.commit()

        logger.info(f'K6脚本生成成功, 脚本ID: {script.script_id}')

        return {
            'script_id': script.script_id,
            'script_name': script.script_name,
            'script_content': script_content,
            'script_url': script_url,
            'config': cfg,
            'thread_id': agent_result.get('thread_id'),
        }
    
    @staticmethod
    async def execute_k6_test(
        db: AsyncSession,
        user_id: int,
        script_id: int,
        config: Optional[Dict] = None,
    ) -> Dict:
        """
        执行K6性能测试

        流程:
        1. 获取脚本信息
        2. 保存脚本到k6_agent workspace并提交执行
        3. 创建执行记录
        4. 返回执行ID和任务ID
        """
        script = await ScriptDAO.get_by_id(db, script_id)
        if not script:
            raise ValueError(f'脚本不存在: {script_id}')

        cfg = config or {}

        # 创建执行记录（待运行）
        execution = TestExecution(
            script_id=script_id,
            project_id=script.project_id,
            execution_type='k6',
            execution_status='pending',
            config=json.dumps(cfg),
            create_by=str(user_id),
        )

        db.add(execution)
        await db.flush()
        await db.refresh(execution)

        # 保存脚本到k6 workspace并提交执行
        runner = get_k6_runner()
        virtual_path, actual_path = runner.save_script(
            script.script_name,
            script.script_content or '',
            project_id=script.project_id,
            requirement_id=script.requirement_id,
        )
        start_time = datetime.now()
        task_id = runner.submit_and_monitor(virtual_path, execution.execution_id)

        # 更新执行记录为运行中
        await ExecutionDAO.update_status(
            db,
            execution.execution_id,
            'running',
            start_time=start_time,
            thread_id=task_id,
            agent_id='k6_agent',
            result={'script_path': virtual_path, 'actual_path': str(actual_path)},
        )
        await db.commit()

        logger.info(f'提交K6测试任务, 执行ID: {execution.execution_id}, task_id: {task_id}')

        return {
            'execution_id': execution.execution_id,
            'task_id': task_id,
            'status': 'running',
            'message': 'K6测试已提交，正在执行中',
        }

    @staticmethod
    async def get_execution_status(db: AsyncSession, execution_id: int) -> Dict:
        """获取执行状态"""
        execution = await ExecutionDAO.get_by_id(db, execution_id)
        if not execution:
            raise ValueError(f'执行记录不存在: {execution_id}')

        return {
            'execution_id': execution.execution_id,
            'status': execution.execution_status,
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'error_message': execution.error_message,
            'result_url': execution.result_url,
        }

    @staticmethod
    async def stream_execution_logs(
        db: AsyncSession,
        execution_id: int,
    ) -> AsyncGenerator[Dict, None]:
        """
        流式推送执行日志（SSE）
        逻辑：基于 ExecutionDAO 状态 + k6 任务进度轮询
        """
        execution = await ExecutionDAO.get_by_id(db, execution_id)
        if not execution:
            raise ValueError(f'执行记录不存在: {execution_id}')

        runner = get_k6_runner()
        task_id = execution.thread_id

        # 如果没有task_id，直接推送一次状态
        if not task_id:
            yield {
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': f'当前状态: {execution.execution_status}',
            }
            return

        while True:
            status = runner.manager.get_task_status(task_id)
            if not status:
                yield {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'error',
                    'message': f'任务不存在: {task_id}',
                }
                break

            yield {
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': f"任务状态: {status.get('status')}, 进度: {status.get('progress', 0)}%",
                'detail': status,
            }

            if status.get('status') in ('completed', 'failed', 'cancelled'):
                break

            await asyncio.sleep(2)

    @staticmethod
    async def download_report(db: AsyncSession, report_id: int) -> Dict:
        """下载报告"""
        report = await ReportDAO.get_by_id(db, report_id)
        if not report:
            raise ValueError(f'报告不存在: {report_id}')

        # 从MinIO获取报告文件
        minio_client = MinIOClient()
        file_content = await minio_client.download_file(report.report_url)

        # 根据文件名简单判断类型
        filename = f'k6_report_{report_id}'
        media_type = 'application/json'
        if report.report_url and str(report.report_url).lower().endswith('.html'):
            filename += '.html'
            media_type = 'text/html'
        else:
            filename += '.json'

        return {
            'content': file_content,
            'filename': filename,
            'media_type': media_type,
        }
