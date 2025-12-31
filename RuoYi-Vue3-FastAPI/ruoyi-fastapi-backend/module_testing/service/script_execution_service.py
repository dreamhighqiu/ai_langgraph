"""
脚本执行服务 - 基于 LangGraph API 实现真实执行
"""
import json
import asyncio
from typing import Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.script_dao import ScriptDAO
from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.report_dao import ReportDAO
from module_testing.agents.agent_manager import get_agent_manager
from utils.log_util import logger


class ScriptExecutionService:
    """脚本执行服务 - 负责调用Agent执行脚本并管理执行记录"""
    
    @staticmethod
    async def execute_script(
        db: AsyncSession,
        script_id: int,
        execution_config: Optional[dict] = None,
        current_user: str = ''
    ) -> dict:
        """
        执行脚本 - 完整流程实现
        
        流程�?
        1. 获取脚本详情
        2. 创建执行记录
        3. 根据脚本类型选择Agent
        4. 调用LangGraph API执行
        5. 更新执行状�?
        6. 生成报告
        
        Args:
            db: 数据库会�?
            script_id: 脚本ID
            execution_config: 执行配置
            current_user: 当前用户
            
        Returns:
            执行结果
        """
        try:
            # 1. 获取脚本详情
            script = await ScriptDAO.get_script_by_id(db, script_id)
            if not script:
                return {
                    'success': False,
                    'error': f"脚本不存�? {script_id}"
                }
            
            # 提取属�?
            script_name = script.script_name
            script_type = script.script_type
            script_path = script.script_path
            script_content = script.script_content
            project_id = script.project_id
            
            logger.info(f"开始执行脚�? {script_name} [ID: {script_id}, 类型: {script_type}]")
            
            # 2. 创建执行记录
            execution_data = {
                'project_id': project_id,
                'script_id': script_id,
                'execution_type': script_type,
                'execution_env': 'langgraph_api',
                'execution_config': json.dumps(execution_config or {}),
                'execution_status': '1',  # 执行�?
                'start_time': datetime.now(),
                'trigger_type': 'manual',
                'trigger_user': current_user,
                'create_by': current_user,
                'create_time': datetime.now()
            }
            
            execution = await ExecutionDAO.add_execution(db, execution_data)
            await db.commit()
            await db.refresh(execution)
            
            execution_id = execution.execution_id
            logger.info(f"创建执行记录: ID {execution_id}")
            
            # 3. 根据脚本类型选择Agent
            agent_mapping = {
                'k6': 'k6_agent',
                'playwright': 'ui_automation_agent',
                'api': 'rest_api_agent'
            }
            agent_id = agent_mapping.get(script_type)
            
            if not agent_id:
                # 更新执行状态为失败
                await ExecutionDAO.update_execution(db, execution_id, {
                    'execution_status': '3',
                    'end_time': datetime.now(),
                    'execution_result': json.dumps({'error': f'不支持的脚本类型: {script_type}'})
                })
                await db.commit()
                
                return {
                    'success': False,
                    'error': f'不支持的脚本类型: {script_type}',
                    'execution_id': execution_id
                }
            
            try:
                # 4. 调用Agent执行脚本
                agent_manager = get_agent_manager()
                
                # 构建执行提示（包含脚本内容）
                execution_prompt = f"""请执行以下{script_type}测试脚本�?

脚本名称: {script_name}
脚本类型: {script_type}

脚本内容:
```
{script_content}
```

执行配置:
{json.dumps(execution_config or {}, ensure_ascii=False, indent=2)}

请执行测试并返回详细的测试结果，包括�?
1. 执行状态（成功/失败�?
2. 测试指标和数�?
3. 错误信息（如果有�?
4. 测试报告
"""
                
                logger.info(f"调用Agent [{agent_id}] 执行脚本")
                
                # 执行脚本
                execution_result = await agent_manager.execute_script(
                    agent_id=agent_id,
                    script_path=script_path,
                    config=execution_config
                )
                
                # 5. 更新执行记录
                end_time = datetime.now()
                duration = int((end_time - execution.start_time).total_seconds())
                
                if execution_result.get('success'):
                    # 执行成功
                    output = execution_result.get('output', '')
                    thread_id = execution_result.get('thread_id')
                    
                    update_data = {
                        'execution_status': '2',  # 成功
                        'end_time': end_time,
                        'duration': duration,
                        'execution_log': output,
                        'execution_result': json.dumps({
                            'success': True,
                            'output': output,
                            'agent_id': agent_id,
                            'thread_id': thread_id
                        }, ensure_ascii=False)
                    }
                    
                    await ExecutionDAO.update_execution(db, execution_id, update_data)
                    await db.commit()
                    
                    logger.info(f"脚本执行成功: {script_name}, 耗时: {duration}s")
                    
                    # 6. 生成报告
                    try:
                        report_result = await ScriptExecutionService._generate_report(
                            db=db,
                            execution_id=execution_id,
                            script_id=script_id,
                            execution_output=output,
                            script_type=script_type,
                            current_user=current_user
                        )
                        
                        logger.info(f"测试报告已生成: {report_result.get('report_id')}")
                        
                    except Exception as e:
                        logger.warning(f"生成报告失败: {e}")
                    
                    return {
                        'success': True,
                        'execution_id': execution_id,
                        'script_name': script_name,
                        'duration': duration,
                        'output': output,
                        'agent_id': agent_id,
                        'thread_id': thread_id,
                        'message': f'{script_type}脚本执行成功'
                    }
                    
                else:
                    # 执行失败
                    error = execution_result.get('error', '执行失败')
                    
                    update_data = {
                        'execution_status': '3',  # 失败
                        'end_time': end_time,
                        'duration': duration,
                        'execution_log': f"错误: {error}",
                        'execution_result': json.dumps({
                            'success': False,
                            'error': error,
                            'agent_id': agent_id
                        }, ensure_ascii=False)
                    }
                    
                    await ExecutionDAO.update_execution(db, execution_id, update_data)
                    await db.commit()
                    
                    logger.error(f"脚本执行失败: {script_name}, 错误: {error}")
                    
                    return {
                        'success': False,
                        'execution_id': execution_id,
                        'error': error,
                        'agent_id': agent_id,
                        'message': f'{script_type}脚本执行失败'
                    }
                    
            except Exception as e:
                # 异常处理
                end_time = datetime.now()
                duration = int((end_time - execution.start_time).total_seconds())
                error_msg = str(e)
                
                update_data = {
                    'execution_status': '3',
                    'end_time': end_time,
                    'duration': duration,
                    'execution_log': f"异常: {error_msg}",
                    'execution_result': json.dumps({
                        'success': False,
                        'error': error_msg
                    }, ensure_ascii=False)
                }
                
                await ExecutionDAO.update_execution(db, execution_id, update_data)
                await db.commit()
                
                logger.error(f"脚本执行异常: {script_name}, 异常: {e}", exc_info=True)
                
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'error': error_msg,
                    'message': '脚本执行异常'
                }
                
        except Exception as e:
            logger.error(f"执行脚本失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def _generate_report(
        db: AsyncSession,
        execution_id: int,
        script_id: int,
        execution_output: str,
        script_type: str,
        current_user: str
    ) -> dict:
        """
        从执行输出生成测试报�?
        
        Args:
            db: 数据库会�?
            execution_id: 执行ID
            script_id: 脚本ID
            execution_output: 执行输出
            script_type: 脚本类型
            current_user: 当前用户
            
        Returns:
            报告信息
        """
        try:
            # 提取测试结果和指�?
            report_data = {
                'execution_id': execution_id,
                'script_id': script_id,
                'report_type': script_type,
                'report_format': 'json',
                'test_result': '2',  # 默认通过，可以根据输出解�?
                'test_summary': json.dumps({
                    'execution_output': execution_output[:1000],  # 截取�?000字符
                    'script_type': script_type,
                    'generated_at': datetime.now().isoformat()
                }, ensure_ascii=False),
                'report_data': json.dumps({
                    'full_output': execution_output,
                    'metrics': {},  # 可以从输出中解析指标
                    'errors': [],
                    'warnings': []
                }, ensure_ascii=False),
                'create_by': current_user,
                'create_time': datetime.now()
            }
            
            report = await ReportDAO.add_report(db, report_data)
            await db.commit()
            await db.refresh(report)
            
            return {
                'success': True,
                'report_id': report.report_id
            }
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def cancel_execution(
        db: AsyncSession,
        execution_id: int,
        current_user: str = ''
    ) -> dict:
        """
        取消执行（尽力而为，LangGraph可能不支持中断）
        
        Args:
            db: 数据库会�?
            execution_id: 执行ID
            current_user: 当前用户
            
        Returns:
            操作结果
        """
        try:
            execution = await ExecutionDAO.get_execution_by_id(db, execution_id)
            if not execution:
                return {
                    'success': False,
                    'error': f"执行记录不存�? {execution_id}"
                }
            
            # 只能取消"执行�?状态的任务
            if execution.execution_status != '1':
                return {
                    'success': False,
                    'error': '只能取消执行中的任务'
                }
            
            # 更新状态为已取�?
            update_data = {
                'execution_status': '4',  # 已取�?
                'end_time': datetime.now(),
                'update_by': current_user,
                'update_time': datetime.now(),
                'execution_log': f"{execution.execution_log or ''}\n\n[{datetime.now().isoformat()}] 用户取消执行"
            }
            
            await ExecutionDAO.update_execution(db, execution_id, update_data)
            await db.commit()
            
            logger.info(f"取消执行成功: ID {execution_id}")
            
            return {
                'success': True,
                'execution_id': execution_id,
                'message': '已标记为取消状态（实际执行可能仍在进行）'
            }
            
        except Exception as e:
            logger.error(f"取消执行失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def retry_execution(
        db: AsyncSession,
        execution_id: int,
        current_user: str = ''
    ) -> dict:
        """
        重试执行
        
        Args:
            db: 数据库会�?
            execution_id: 执行ID
            current_user: 当前用户
            
        Returns:
            新的执行ID
        """
        try:
            # 获取原执行记�?
            execution = await ExecutionDAO.get_execution_by_id(db, execution_id)
            if not execution:
                return {
                    'success': False,
                    'error': f"执行记录不存�? {execution_id}"
                }
            
            script_id = execution.script_id
            execution_config = json.loads(execution.execution_config) if execution.execution_config else {}
            
            # 调用执行脚本（会创建新的执行记录�?
            result = await ScriptExecutionService.execute_script(
                db=db,
                script_id=script_id,
                execution_config=execution_config,
                current_user=current_user
            )
            
            return result
            
        except Exception as e:
            logger.error(f"重试执行失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

