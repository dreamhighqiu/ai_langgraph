"""
测试脚本服务 - 业务逻辑层
"""
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.agents.agent_manager import get_agent_manager
from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.project_dao import ProjectDAO
from module_testing.dao.script_dao import ScriptDAO
from module_testing.entity.do.execution_do import TestExecution
from module_testing.entity.do.script_do import TestScript
from module_testing.entity.vo.script_vo import (
    AddScriptModel,
    DeleteScriptModel,
    EditScriptModel,
    ExecuteScriptModel,
    GenerateScriptModel,
    ScriptModel,
    ScriptPageQueryModel,
)
from module_testing.storage.minio_client import get_minio_client
from utils.log_util import logger
from module_testing.agents.k6_runner import get_k6_runner
from module_ui_testing.service.integration import (
    get_agent_id_for_script_type,
    get_requirement_type_for_script_type,
    get_script_file_ext,
    try_execute_ui_script,
)


class ScriptService:
    """测试脚本服务"""
    
    @staticmethod
    async def get_script_list(
        db: AsyncSession,
        query: ScriptPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取脚本列表"""
        scripts, total = await ScriptDAO.get_list(db, query, is_page)
        
        return {
            'rows': scripts,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_script_by_id(db: AsyncSession, script_id: int) -> dict | None:
        """获取脚本详情"""
        result = await ScriptDAO.get_with_project(db, script_id)
        if result:
            script = result['script']
            return {
                'script_id': script.script_id,
                'project_id': script.project_id,
                'project_name': result['project_name'],
                'script_name': script.script_name,
                'script_type': script.script_type,
                'script_content': script.script_content,
                'script_file_path': script.script_file_path,
                'version': script.version,
                'config': script.config,
                'agent_id': script.agent_id,
                'generation_prompt': script.generation_prompt,
                'create_by': script.create_by,
                'create_time': script.create_time,
                'update_by': script.update_by,
                'update_time': script.update_time,
                'status': script.status,
                'remark': script.remark,
            }
        return None
    
    @staticmethod
    async def create_script(
        db: AsyncSession,
        model: AddScriptModel,
        create_by: str
    ) -> dict[str, Any]:
        """创建脚本"""
        try:
            # 检查项目是否存在
            project = await ProjectDAO.get_by_id(db, model.project_id)
            if not project:
                return {
                    'success': False,
                    'error': '项目不存在'
                }
            
            # 创建脚本
            script = TestScript(
                project_id=model.project_id,
                script_name=model.script_name,
                script_type=model.script_type,
                script_content=model.script_content,
                config=model.config,
                remark=model.remark,
                create_by=create_by
            )
            
            # 保存脚本内容到MinIO
            if model.script_content:
                minio_client = get_minio_client()
                override_ext = get_script_file_ext(model.script_type)
                file_ext = override_ext or {'k6': 'js', 'api': 'py'}.get(model.script_type, 'txt')
                object_path = f"scripts/{model.script_type}/project_{model.project_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                
                success, path = minio_client.upload_file(
                    file_content=model.script_content.encode('utf-8'),
                    object_name=object_path,
                    content_type='text/plain'
                )
                
                if success:
                    script.script_file_path = path
            
            created = await ScriptDAO.create(db, script)
            created_id = created.script_id  # 立即提取
            created_name = created.script_name
            await db.commit()
            
            logger.info(f'创建脚本成功: {created_id} - {created_name}')
            
            return {
                'success': True,
                'script_id': created_id
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'创建脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def generate_script(
        db: AsyncSession,
        model: GenerateScriptModel,
        create_by: str
    ) -> dict[str, Any]:
        """AI生成测试脚本"""
        try:
            # 检查项目是否存在
            project = await ProjectDAO.get_by_id(db, model.project_id)
            if not project:
                return {
                    'success': False,
                    'error': '项目不存在'
                }
            
            # 映射脚本类型到Agent类型
            agent_type_map = {'k6': 'k6_agent', 'api': 'rest_api_agent'}
            agent_type = agent_type_map.get(model.script_type) or get_agent_id_for_script_type(model.script_type)
            
            if not agent_type:
                return {
                    'success': False,
                    'error': f'不支持的脚本类型: {model.script_type}'
                }

            # 构造需求信息供 Agent 生成脚本（使用脚本名称+提示词）
            requirement = {
                'requirement_id': None,
                'requirement_name': model.script_name,
                'requirement_type': {'k6': 'performance', 'api': 'api'}.get(model.script_type)
                or get_requirement_type_for_script_type(model.script_type)
                or 'api',
                'description': model.prompt,
                'acceptance_criteria': model.config or {}
            }
            
            # 调用Agent生成脚本
            agent_manager = get_agent_manager()
            result = await agent_manager.generate_script(
                agent_id=agent_type,
                requirement=requirement,
                config=model.config
            )
            
            if not result['success']:
                return result
            
            script_content = result['script_content']
            
            # 保存脚本内容到MinIO
            minio_client = get_minio_client()
            override_ext = get_script_file_ext(model.script_type)
            file_ext = override_ext or {'k6': 'js', 'api': 'py'}.get(model.script_type, 'txt')
            object_path = f"scripts/{model.script_type}/project_{model.project_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
            
            success, path = minio_client.upload_file(
                file_content=script_content.encode('utf-8'),
                object_name=object_path,
                content_type='text/plain'
            )
            
            if not success:
                logger.warning(f'保存脚本到MinIO失败: {path}')
                path = None
            
            # 保存脚本记录到数据库
            script = TestScript(
                project_id=model.project_id,
                script_name=model.script_name,
                script_type=model.script_type,
                script_content=script_content,
                script_file_path=path,
                agent_id=result.get('agent_id'),
                generation_prompt=model.prompt,
                config=model.config,
                create_by=create_by
            )
            
            created_script = await ScriptDAO.create(db, script)
            created_script_id = created_script.script_id  # 立即提取ID
            await db.commit()
            
            logger.info(f'AI生成脚本成功: {created_script_id}')
            
            return {
                'success': True,
                'script_id': created_script_id,
                'script_content': script_content,
                'file_path': path,
                'thread_id': result.get('thread_id'),
                'agent_id': result.get('agent_id')
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'AI生成脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def update_script(
        db: AsyncSession,
        model: EditScriptModel,
        update_by: str
    ) -> dict[str, Any]:
        """更新脚本"""
        try:
            # 检查脚本是否存在
            script = await ScriptDAO.get_by_id(db, model.script_id)
            if not script:
                return {
                    'success': False,
                    'error': '脚本不存在'
                }
            
            # 立即提取需要的值，避免后续异步操作中访问ORM对象导致greenlet错误
            script_type = script.script_type
            project_id = script.project_id
            current_version = script.version or '1.0.0'
            
            # 构建更新字段
            update_data = {'update_by': update_by}
            if model.script_name is not None:
                update_data['script_name'] = model.script_name
            if model.script_content is not None:
                update_data['script_content'] = model.script_content
                
                # 更新MinIO中的脚本文件
                if model.script_content:
                    minio_client = get_minio_client()
                    override_ext = get_script_file_ext(script_type)
                    file_ext = override_ext or {'k6': 'js', 'api': 'py'}.get(script_type, 'txt')
                    object_path = f"scripts/{script_type}/project_{project_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                    
                    success, path = minio_client.upload_file(
                        file_content=model.script_content.encode('utf-8'),
                        object_name=object_path,
                        content_type='text/plain'
                    )
                    
                    if success:
                        update_data['script_file_path'] = path
                        # 更新版本号
                        parts = current_version.split('.')
                        parts[-1] = str(int(parts[-1]) + 1)
                        update_data['version'] = '.'.join(parts)
            
            if model.config is not None:
                update_data['config'] = model.config
            if model.status is not None:
                update_data['status'] = model.status
            if model.remark is not None:
                update_data['remark'] = model.remark
            
            await ScriptDAO.update_by_id(db, model.script_id, **update_data)
            await db.commit()
            
            logger.info(f'更新脚本成功: {model.script_id}')
            
            return {'success': True}
        
        except Exception as e:
            await db.rollback()
            logger.error(f'更新脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def delete_scripts(
        db: AsyncSession,
        model: DeleteScriptModel
    ) -> dict[str, Any]:
        """删除脚本"""
        try:
            script_ids = [int(id) for id in model.script_ids.split(',') if id.strip()]
            
            if not script_ids:
                return {
                    'success': False,
                    'error': '请选择要删除的脚本'
                }
            
            # 检查脚本是否有执行记录
            for script_id in script_ids:
                exec_count = await ExecutionDAO.count_by_script(db, script_id)
                if exec_count > 0:
                    script = await ScriptDAO.get_by_id(db, script_id)
                    script_name = script.script_name if script else f'ID:{script_id}'
                    return {
                        'success': False,
                        'error': f'脚本[{script_name}]存在{exec_count}条执行记录，无法删除'
                    }
            
            # 执行删除
            count = await ScriptDAO.delete_by_ids(db, script_ids)
            await db.commit()
            
            logger.info(f'删除脚本成功: 共{count}个')
            
            return {
                'success': True,
                'count': count
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'删除脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def execute_script(
        db: AsyncSession,
        model: ExecuteScriptModel,
        executor: str
    ) -> dict[str, Any]:
        """执行脚本"""
        try:
            # 获取脚本信息
            script = await ScriptDAO.get_by_id(db, model.script_id)
            if not script:
                return {
                    'success': False,
                    'error': '脚本不存在'
                }
            
            if script.status != '0':
                return {
                    'success': False,
                    'error': '脚本已停用，无法执行'
                }
            
            # 立即提取需要的值，避免后续异步操作中访问ORM对象导致greenlet错误
            script_type = script.script_type
            script_content = script.script_content
            script_name = script.script_name
            
            # 创建执行记录
            execution = TestExecution(
                script_id=model.script_id,
                execution_type=model.execution_type or 'manual',
                execution_status='pending',
                config=model.config,
                executor=executor
            )
            
            created_execution = await ExecutionDAO.create(db, execution)
            execution_id = created_execution.execution_id  # 提取ID
            await db.commit()
            
            ui_result = await try_execute_ui_script(
                db=db,
                execution_id=execution_id,
                script=script,
                execution_config=model.config,
                executor=executor,
            )
            if ui_result is not None:
                return ui_result

            # 保存脚本到 k6_agent workspace 并提交执行任务
            if script_type != 'k6':
                return {
                    'success': False,
                    'error': f'当前脚本类型[{script_type}]暂未实现执行',
                    'execution_id': execution_id
                }

            runner = get_k6_runner()
            virtual_path, actual_path = runner.save_script(
                script_name,
                script_content or '',
                project_id=script.project_id,
                requirement_id=script.requirement_id,
            )
            start_time = datetime.now()
            task_id = runner.submit_and_monitor(virtual_path, execution_id)

            # 更新执行记录为运行中，写入 thread_id/agent_id/开始时间/文件路径
            await ExecutionDAO.update_status(
                db, execution_id,
                'running',
                start_time=start_time,
                thread_id=task_id,
                agent_id='k6_agent',
                result={'script_path': virtual_path, 'actual_path': str(actual_path)}
            )
            await db.commit()
            
            logger.info(f'执行脚本: {model.script_id}, execution_id: {execution_id}')
            
            return {
                'success': True,
                'execution_id': execution_id
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'执行脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }

