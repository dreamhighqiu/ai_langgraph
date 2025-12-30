"""
测试项目服务 - 业务逻辑层
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.project_dao import ProjectDAO
from module_testing.dao.script_dao import ScriptDAO
from module_testing.entity.do.project_do import TestProject
from module_testing.entity.vo.project_vo import (
    AddProjectModel,
    DeleteProjectModel,
    EditProjectModel,
    ProjectModel,
    ProjectPageQueryModel,
)
from utils.log_util import logger


class ProjectService:
    """测试项目服务"""
    
    @staticmethod
    async def get_project_list(
        db: AsyncSession,
        query: ProjectPageQueryModel,
        is_page: bool = True
    ) -> dict[str, Any]:
        """获取项目列表"""
        projects, total = await ProjectDAO.get_list(db, query, is_page)
        
        rows = [ProjectModel.model_validate(p) for p in projects]
        
        return {
            'rows': rows,
            'total': total,
            'page_num': query.page_num,
            'page_size': query.page_size
        }
    
    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: int) -> ProjectModel | None:
        """获取项目详情"""
        project = await ProjectDAO.get_by_id(db, project_id)
        if project:
            return ProjectModel.model_validate(project)
        return None
    
    @staticmethod
    async def get_all_projects(db: AsyncSession, status: str = None) -> list[ProjectModel]:
        """获取所有项目(下拉选择用)"""
        projects = await ProjectDAO.get_all(db, status)
        return [ProjectModel.model_validate(p) for p in projects]
    
    @staticmethod
    async def create_project(
        db: AsyncSession,
        model: AddProjectModel,
        create_by: str
    ) -> dict[str, Any]:
        """创建项目"""
        try:
            # 检查项目名称是否唯一
            is_unique = await ProjectDAO.check_name_unique(db, model.project_name)
            if not is_unique:
                return {
                    'success': False,
                    'error': f'项目名称[{model.project_name}]已存在'
                }
            
            # 创建项目
            project = TestProject(
                project_name=model.project_name,
                project_type=model.project_type,
                description=model.description,
                status=model.status or '0',
                remark=model.remark,
                create_by=create_by
            )
            
            created = await ProjectDAO.create(db, project)
            # 立即提取属性，避免commit后访问ORM对象
            created_id = created.project_id
            created_name = created.project_name
            project_model = ProjectModel.model_validate(created)
            await db.commit()
            
            logger.info(f'创建项目成功: {created_id} - {created_name}')
            
            return {
                'success': True,
                'project_id': created_id,
                'project': project_model
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'创建项目失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def update_project(
        db: AsyncSession,
        model: EditProjectModel,
        update_by: str
    ) -> dict[str, Any]:
        """更新项目"""
        try:
            # 检查项目是否存在
            project = await ProjectDAO.get_by_id(db, model.project_id)
            if not project:
                return {
                    'success': False,
                    'error': '项目不存在'
                }
            
            # 立即提取属性
            current_name = project.project_name
            
            # 检查名称唯一性
            if model.project_name and model.project_name != current_name:
                is_unique = await ProjectDAO.check_name_unique(
                    db, model.project_name, model.project_id
                )
                if not is_unique:
                    return {
                        'success': False,
                        'error': f'项目名称[{model.project_name}]已存在'
                    }
            
            # 构建更新字段
            update_data = {'update_by': update_by}
            if model.project_name is not None:
                update_data['project_name'] = model.project_name
            if model.project_type is not None:
                update_data['project_type'] = model.project_type
            if model.description is not None:
                update_data['description'] = model.description
            if model.status is not None:
                update_data['status'] = model.status
            if model.remark is not None:
                update_data['remark'] = model.remark
            
            await ProjectDAO.update_by_id(db, model.project_id, **update_data)
            await db.commit()
            
            logger.info(f'更新项目成功: {model.project_id}')
            
            return {'success': True}
        
        except Exception as e:
            await db.rollback()
            logger.error(f'更新项目失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def delete_projects(
        db: AsyncSession,
        model: DeleteProjectModel
    ) -> dict[str, Any]:
        """删除项目"""
        try:
            project_ids = [int(id) for id in model.project_ids.split(',') if id.strip()]
            
            if not project_ids:
                return {
                    'success': False,
                    'error': '请选择要删除的项目'
                }
            
            # 检查项目下是否有脚本
            for project_id in project_ids:
                script_count = await ScriptDAO.count_by_project(db, project_id)
                if script_count > 0:
                    project = await ProjectDAO.get_by_id(db, project_id)
                    project_name = project.project_name if project else f'ID:{project_id}'
                    return {
                        'success': False,
                        'error': f'项目[{project_name}]下存在{script_count}个脚本，无法删除'
                    }
            
            # 执行删除
            count = await ProjectDAO.delete_by_ids(db, project_ids)
            await db.commit()
            
            logger.info(f'删除项目成功: 共{count}个')
            
            return {
                'success': True,
                'count': count
            }
        
        except Exception as e:
            await db.rollback()
            logger.error(f'删除项目失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    async def change_status(
        db: AsyncSession,
        project_id: int,
        status: str,
        update_by: str
    ) -> dict[str, Any]:
        """修改项目状态"""
        try:
            project = await ProjectDAO.get_by_id(db, project_id)
            if not project:
                return {
                    'success': False,
                    'error': '项目不存在'
                }
            
            await ProjectDAO.update_by_id(
                db, project_id,
                status=status,
                update_by=update_by
            )
            await db.commit()
            
            logger.info(f'修改项目状态: {project_id} -> {status}')
            
            return {'success': True}
        
        except Exception as e:
            await db.rollback()
            logger.error(f'修改项目状态失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }

