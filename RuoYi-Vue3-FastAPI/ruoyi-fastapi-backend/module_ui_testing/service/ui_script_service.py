"""
UI自动化测试脚本服务 - 业务逻辑层
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_ui_testing.dao.ui_script_dao import UIScriptDAO
from module_ui_testing.entity.do.ui_script_do import UITestScript
from module_ui_testing.entity.vo.ui_script_vo import (
    AddUIScriptModel,
    DeleteUIScriptModel,
    EditUIScriptModel,
    UIScriptModel,
    UIScriptPageQueryModel,
)
from utils.log_util import logger


class UIScriptService:
    """UI自动化测试脚本服务"""
    
    @staticmethod
    async def get_script_list(
        db: AsyncSession,
        query: UIScriptPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取脚本列表"""
        scripts, total = await UIScriptDAO.get_list(db, query, is_page)
        
        rows = [UIScriptModel.model_validate(s) for s in scripts]
        
        return {
            'rows': rows,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_script_by_id(db: AsyncSession, script_id: int) -> dict[str, Any] | None:
        """获取脚本详情（包含项目和需求信息）"""
        result = await UIScriptDAO.get_with_project(db, script_id)
        if result:
            script_data = {
                'script_id': result['script'].script_id,
                'project_id': result['script'].project_id,
                'project_name': result['project_name'],
                'requirement_id': result['script'].requirement_id,
                'requirement_name': result['requirement_name'],
                'script_name': result['script'].script_name,
                'script_type': result['script'].script_type,
                'language': result['script'].language,
                'browser': result['script'].browser,
                'script_content': result['script'].script_content,
                'script_file_path': result['script'].script_file_path,
                'version': result['script'].version,
                'config': result['script'].config,
                'agent_id': result['script'].agent_id,
                'generation_prompt': result['script'].generation_prompt,
                'use_rag': result['script'].use_rag,
                'status': result['script'].status,
                'create_by': result['script'].create_by,
                'create_time': result['script'].create_time,
                'update_by': result['script'].update_by,
                'update_time': result['script'].update_time,
                'remark': result['script'].remark,
            }
            return script_data
        return None
    
    @staticmethod
    async def create_script(
        db: AsyncSession,
        model: AddUIScriptModel,
        create_by: str
    ) -> dict[str, Any]:
        """创建脚本"""
        try:
            # 创建脚本
            script = UITestScript(
                project_id=model.project_id,
                requirement_id=model.requirement_id,
                script_name=model.script_name,
                script_type='playwright',
                language=model.language,
                browser=model.browser,
                script_content=model.script_content,
                script_file_path=model.script_file_path,
                version=model.version,
                config=model.config,
                agent_id=model.agent_id,
                generation_prompt=model.generation_prompt,
                use_rag=model.use_rag,
                status=model.status or '0',
                remark=model.remark,
                create_by=create_by
            )
            
            created = await UIScriptDAO.create(db, script)
            created_id = created.script_id
            created_name = created.script_name
            script_model = UIScriptModel.model_validate(created)
            await db.commit()
            
            logger.info(f'创建UI自动化脚本成功: {created_id} - {created_name}')
            
            return {
                'success': True,
                'script_id': created_id,
                'script': script_model
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'创建UI自动化脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def update_script(
        db: AsyncSession,
        model: EditUIScriptModel,
        update_by: str
    ) -> dict[str, Any]:
        """更新脚本"""
        try:
            # 检查脚本是否存在
            script = await UIScriptDAO.get_by_id(db, model.script_id)
            if not script:
                return {
                    'success': False,
                    'error': f'脚本不存在: {model.script_id}'
                }
            
            # 准备更新数据
            update_data = {
                'update_by': update_by
            }
            
            if model.script_name is not None:
                update_data['script_name'] = model.script_name
            if model.language is not None:
                update_data['language'] = model.language
            if model.browser is not None:
                update_data['browser'] = model.browser
            if model.script_content is not None:
                update_data['script_content'] = model.script_content
            if model.script_file_path is not None:
                update_data['script_file_path'] = model.script_file_path
            if model.version is not None:
                update_data['version'] = model.version
            if model.config is not None:
                update_data['config'] = model.config
            if model.requirement_id is not None:
                update_data['requirement_id'] = model.requirement_id
            if model.status is not None:
                update_data['status'] = model.status
            if model.remark is not None:
                update_data['remark'] = model.remark
            
            # 更新脚本
            success = await UIScriptDAO.update_by_id(db, model.script_id, **update_data)
            
            if success:
                await db.commit()
                logger.info(f'更新UI自动化脚本成功: {model.script_id}')
                return {
                    'success': True,
                    'script_id': model.script_id
                }
            else:
                await db.rollback()
                return {
                    'success': False,
                    'error': '更新失败'
                }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'更新UI自动化脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def delete_scripts(
        db: AsyncSession,
        model: DeleteUIScriptModel
    ) -> dict[str, Any]:
        """批量删除脚本"""
        try:
            count = await UIScriptDAO.delete_by_ids(db, model.script_ids)
            await db.commit()
            
            logger.info(f'删除UI自动化脚本成功: {count}个')
            return {
                'success': True,
                'count': count
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'删除UI自动化脚本失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def get_scripts_by_project(
        db: AsyncSession,
        project_id: int
    ) -> list[UIScriptModel]:
        """获取项目下的所有脚本"""
        scripts = await UIScriptDAO.get_by_project(db, project_id)
        return [UIScriptModel.model_validate(s) for s in scripts]
    
    @staticmethod
    async def count_scripts_by_project(
        db: AsyncSession,
        project_id: int
    ) -> int:
        """统计项目下的脚本数量"""
        return await UIScriptDAO.count_by_project(db, project_id)

