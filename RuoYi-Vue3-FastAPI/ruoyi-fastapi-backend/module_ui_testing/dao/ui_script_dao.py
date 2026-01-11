"""
UI自动化测试脚本DAO - 数据访问层
"""
import json
from typing import Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.project_do import TestProject
from module_testing.entity.do.requirement_do import TestRequirement
from module_ui_testing.entity.do.ui_script_do import UITestScript
from module_ui_testing.entity.vo.ui_script_vo import UIScriptPageQueryModel


class UIScriptDAO:
    """UI自动化测试脚本数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, script_id: int) -> Optional[UITestScript]:
        """根据ID获取脚本"""
        result = await db.execute(
            select(UITestScript).where(
                and_(
                    UITestScript.script_id == script_id,
                    UITestScript.del_flag == '0'
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_with_project(db: AsyncSession, script_id: int) -> Optional[dict]:
        """获取脚本及项目信息"""
        result = await db.execute(
            select(UITestScript, TestProject.project_name, TestRequirement.requirement_name)
            .join(TestProject, UITestScript.project_id == TestProject.project_id)
            .join(TestRequirement, UITestScript.requirement_id == TestRequirement.requirement_id, isouter=True)
            .where(
                and_(
                    UITestScript.script_id == script_id,
                    UITestScript.del_flag == '0'
                )
            )
        )
        row = result.first()
        if row:
            script, project_name, requirement_name = row
            return {
                'script': script,
                'project_name': project_name,
                'requirement_name': requirement_name,
            }
        return None
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: UIScriptPageQueryModel,
        is_page: bool = True
    ) -> tuple[list[dict], int]:
        """获取脚本列表"""
        # 构建查询条件
        conditions = [UITestScript.del_flag == '0']
        
        if query.project_id:
            conditions.append(UITestScript.project_id == query.project_id)
        if query.script_name:
            conditions.append(UITestScript.script_name.like(f'%{query.script_name}%'))
        if query.language:
            conditions.append(UITestScript.language == query.language)
        if query.browser:
            conditions.append(UITestScript.browser == query.browser)
        if query.requirement_id:
            conditions.append(UITestScript.requirement_id == query.requirement_id)
        if query.status:
            conditions.append(UITestScript.status == query.status)
        if query.agent_id:
            conditions.append(UITestScript.agent_id == query.agent_id)
        if query.begin_time:
            conditions.append(UITestScript.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(UITestScript.create_time <= query.end_time)
        
        # 查询总数
        count_query = select(func.count(UITestScript.script_id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表(关联项目表获取项目名称)
        list_query = (
            select(UITestScript, TestProject.project_name, TestRequirement.requirement_name)
            .join(TestProject, UITestScript.project_id == TestProject.project_id, isouter=True)
            .join(TestRequirement, UITestScript.requirement_id == TestRequirement.requirement_id, isouter=True)
            .where(and_(*conditions))
            .order_by(UITestScript.create_time.desc())
        )
        
        if is_page:
            offset = (query.page_num - 1) * query.page_size
            list_query = list_query.offset(offset).limit(query.page_size)
        
        result = await db.execute(list_query)
        rows = result.all()
        
        scripts = []
        for script, project_name, requirement_name in rows:
            script_dict = {
                'script_id': script.script_id,
                'project_id': script.project_id,
                'project_name': project_name,
                'requirement_id': script.requirement_id,
                'requirement_name': requirement_name,
                'script_name': script.script_name,
                'script_type': script.script_type,
                'language': script.language,
                'browser': script.browser,
                'script_content': script.script_content,
                'script_file_path': script.script_file_path,
                'version': script.version,
                'config': script.config,
                'agent_id': script.agent_id,
                'generation_prompt': script.generation_prompt,
                'use_rag': script.use_rag,
                'create_by': script.create_by,
                'create_time': script.create_time,
                'update_by': script.update_by,
                'update_time': script.update_time,
                'status': script.status,
                'remark': script.remark,
            }
            scripts.append(script_dict)
        
        return scripts, total
    
    @staticmethod
    async def get_by_project(db: AsyncSession, project_id: int) -> list[UITestScript]:
        """获取项目下的所有脚本"""
        result = await db.execute(
            select(UITestScript).where(
                and_(
                    UITestScript.project_id == project_id,
                    UITestScript.del_flag == '0'
                )
            ).order_by(UITestScript.create_time.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, script: UITestScript) -> UITestScript:
        """创建脚本"""
        db.add(script)
        await db.flush()
        await db.refresh(script)
        return script
    
    @staticmethod
    async def update_by_id(db: AsyncSession, script_id: int, **kwargs) -> bool:
        """更新脚本"""
        result = await db.execute(
            update(UITestScript)
            .where(UITestScript.script_id == script_id)
            .values(**kwargs)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_by_ids(db: AsyncSession, script_ids: list[int]) -> int:
        """批量软删除脚本"""
        result = await db.execute(
            update(UITestScript)
            .where(UITestScript.script_id.in_(script_ids))
            .values(del_flag='2')
        )
        return result.rowcount
    
    @staticmethod
    async def update_version(db: AsyncSession, script_id: int, new_version: str) -> bool:
        """更新脚本版本"""
        result = await db.execute(
            update(UITestScript)
            .where(UITestScript.script_id == script_id)
            .values(version=new_version)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def count_by_project(db: AsyncSession, project_id: int) -> int:
        """统计项目下的脚本数量"""
        result = await db.execute(
            select(func.count(UITestScript.script_id)).where(
                and_(
                    UITestScript.project_id == project_id,
                    UITestScript.del_flag == '0'
                )
            )
        )
        return result.scalar() or 0

