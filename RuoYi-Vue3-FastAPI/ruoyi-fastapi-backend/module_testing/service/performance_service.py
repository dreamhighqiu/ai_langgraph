"""
性能测试(K6)专用服务层
"""
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from utils.log_util import logger
from module_testing.agents.langgraph_client import LangGraphClient
from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.report_dao import ReportDAO
from module_testing.dao.requirement_dao import RequirementDAO
from module_testing.dao.script_dao import ScriptDAO
from module_testing.entity.do.execution_do import TestExecution
from module_testing.entity.do.report_do import TestReport
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
        2. 调用testing-agents-service的K6 Agent
        3. 保存生成的脚本到数据库和MinIO
        4. 返回脚本ID和内容
        """
        # 1. 获取需求信息
        requirement = await RequirementDAO.get_by_id(db, requirement_id)
        if not requirement:
            raise ValueError(f'需求不存在: {requirement_id}')
        
        # 2. 准备K6 Agent输入
        config = config or {}
        agent_input = {
            'messages': [
                {
                    'role': 'user',
                    'content': f"""请为以下性能测试需求生成K6脚本:

需求名称: {requirement.requirement_name}
需求描述: {requirement.description}
验收标准: {requirement.acceptance_criteria or '无'}

测试配置:
- 虚拟用户数(VUs): {config.get('vus', 10)}
- 持续时间: {config.get('duration', '30s')}
- 压力阶段: {json.dumps(config.get('stages', []), ensure_ascii=False)}
- 性能阈值: {json.dumps(config.get('thresholds', {}), ensure_ascii=False)}

请生成完整的K6测试脚本，包含详细的性能指标检查。
"""
                }
            ],
            'config': {
                'use_rag': config.get('use_rag', True),
            }
        }
        
        # 3. 调用LangGraph K6 Agent
        logger.info(f'调用K6 Agent生成脚本, 需求ID: {requirement_id}')
        langgraph_client = LangGraphClient()
        agent_result = await langgraph_client.invoke_agent(
            agent_name='k6_agent',
            inputs=agent_input,
        )
        
        # 4. 解析Agent返回的脚本
        script_content = PerformanceService._extract_script_from_agent(agent_result)
        
        # 5. 保存脚本到MinIO
        minio_client = MinIOClient()
        script_filename = f"k6_script_{requirement_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
        script_url = await minio_client.upload_script(
            script_content=script_content,
            filename=script_filename,
        )
        
        # 6. 保存脚本元数据到数据库
        script = TestScript(
            script_name=f"{requirement.requirement_name}_性能测试脚本",
            script_type='k6',
            project_id=requirement.project_id,
            requirement_id=requirement_id,
            script_content=script_content,
            script_url=script_url,
            config=json.dumps(config),
            status='0',  # 未执行
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
            'config': config,
        }
    
    @staticmethod
    def _extract_script_from_agent(agent_result: Dict) -> str:
        """从Agent返回结果中提取K6脚本"""
        # Agent返回格式: {'messages': [...], 'artifacts': {...}}
        # 从最后一条消息或artifacts中提取脚本
        messages = agent_result.get('messages', [])
        
        # 尝试从artifacts获取
        artifacts = agent_result.get('artifacts', {})
        for key, value in artifacts.items():
            if key.startswith('k6_script') or key.endswith('.js'):
                return value
        
        # 从最后一条消息中提取代码块
        if messages:
            last_message = messages[-1]
            content = last_message.get('content', '')
            
            # 提取```javascript或```js代码块
            import re
            pattern = r'```(?:javascript|js)\n(.*?)\n```'
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                return matches[0]
        
        raise ValueError('无法从Agent结果中提取K6脚本')
    
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
        2. 提交到testing-agents-service执行
        3. 创建执行记录
        4. 返回执行ID和状态
        """
        # 1. 获取脚本
        script = await ScriptDAO.get_by_id(db, script_id)
        if not script:
            raise ValueError(f'脚本不存在: {script_id}')

        # 2. 创建执行记录
        execution = TestExecution(
            script_id=script_id,
            project_id=script.project_id,
            execution_type='k6',
            execution_status='running',
            config=json.dumps(config or {}),
            create_by=str(user_id),
        )

        db.add(execution)
        await db.flush()
        await db.refresh(execution)

        # 3. 调用LangGraph K6 Agent执行
        langgraph_client = LangGraphClient()

        # 准备执行任务
        task_input = {
            'messages': [
                {
                    'role': 'user',
                    'content': f'执行K6性能测试脚本: {script.script_name}'
                }
            ],
            'script_content': script.script_content,
            'config': config or {},
        }

        logger.info(f'提交K6测试任务, 执行ID: {execution.execution_id}')

        # 异步执行 - 不等待完成
        asyncio.create_task(
            PerformanceService._run_k6_test_async(
                db=db,
                execution_id=execution.execution_id,
                script=script,
                config=config,
            )
        )

        await db.commit()

        return {
            'execution_id': execution.execution_id,
            'status': 'running',
            'message': 'K6测试已提交，正在执行中',
        }

    @staticmethod
    async def _run_k6_test_async(
        db: AsyncSession,
        execution_id: int,
        script: TestScript,
        config: Optional[Dict],
    ):
        """异步执行K6测试（后台任务）"""
        try:
            # 调用LangGraph执行
            langgraph_client = LangGraphClient()
            result = await langgraph_client.invoke_agent(
                agent_name='k6_agent',
                inputs={
                    'messages': [
                        {
                            'role': 'user',
                            'content': f'执行以下K6脚本:\n\n```javascript\n{script.script_content}\n```'
                        }
                    ]
                }
            )

            # 解析执行结果
            execution_result = PerformanceService._parse_execution_result(result)

            # 保存结果到MinIO
            minio_client = MinIOClient()
            result_filename = f"k6_result_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            result_url = await minio_client.upload_result(
                result_content=json.dumps(execution_result),
                filename=result_filename,
            )

            # 更新执行记录
            execution = await ExecutionDAO.get_by_id(db, execution_id)
            execution.execution_status = 'success' if execution_result.get('success') else 'failed'
            execution.result_url = result_url
            execution.error_message = execution_result.get('error')
            execution.end_time = datetime.now()

            # 生成报告
            report = TestReport(
                execution_id=execution_id,
                script_id=script.script_id,
                project_id=script.project_id,
                report_type='k6_performance',
                report_format='json',
                report_url=result_url,
                summary=json.dumps(execution_result.get('summary', {})),
                create_by=execution.create_by,
            )

            db.add(report)
            await db.commit()

            logger.info(f'K6测试执行完成, 执行ID: {execution_id}, 状态: {execution.execution_status}')

        except Exception as e:
            logger.error(f'K6测试执行失败: {e}')

            # 更新执行状态为失败
            execution = await ExecutionDAO.get_by_id(db, execution_id)
            execution.execution_status = 'failed'
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            await db.commit()

    @staticmethod
    def _parse_execution_result(agent_result: Dict) -> Dict:
        """解析K6执行结果"""
        # 从Agent返回中提取K6结果
        return {
            'success': True,
            'summary': agent_result.get('summary', {}),
            'metrics': agent_result.get('metrics', {}),
            'error': agent_result.get('error'),
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
        }

    @staticmethod
    async def stream_execution_logs(
        db: AsyncSession,
        execution_id: int,
    ) -> AsyncGenerator[Dict, None]:
        """流式推送执行日志（SSE）"""
        execution = await ExecutionDAO.get_by_id(db, execution_id)
        if not execution:
            raise ValueError(f'执行记录不存在: {execution_id}')

        # 模拟日志流（实际应从LangGraph获取）
        for i in range(10):
            await asyncio.sleep(1)
            yield {
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': f'执行进度: {(i+1)*10}%',
            }

    @staticmethod
    async def download_report(db: AsyncSession, report_id: int) -> Dict:
        """下载报告"""
        report = await ReportDAO.get_by_id(db, report_id)
        if not report:
            raise ValueError(f'报告不存在: {report_id}')

        # 从MinIO获取报告文件
        minio_client = MinIOClient()
        file_content = await minio_client.download_file(report.report_url)

        return {
            'content': file_content,
            'filename': f'k6_report_{report_id}.html',
            'media_type': 'text/html',
        }

