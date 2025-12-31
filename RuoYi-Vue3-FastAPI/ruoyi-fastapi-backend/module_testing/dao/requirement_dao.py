"""
测试需求数据访问对象(DAO - Data Access Object)
"""
from typing import List, Optional, Dict, Any

from sqlalchemy import Select, and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.requirement_do import TestRequirement


class RequirementDAO:
    """需求DAO - 统一使用大写DAO命名"""
    
    @staticmethod
    async def get_requirement_by_id(
        db: AsyncSession,
        requirement_id: int
    ) -> Optional[TestRequirement]:
        """
        根据ID获取需求
        
        Args:
            db: 数据库会话
            requirement_id: 需求ID
            
        Returns:
            需求对象
        """
        query = select(TestRequirement).where(
            and_(
                TestRequirement.requirement_id == requirement_id,
                TestRequirement.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_requirements_by_project(
        db: AsyncSession,
        project_id: int,
        requirement_type: Optional[str] = None
    ) -> List[TestRequirement]:
        """
        根据项目ID获取需求列表
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            requirement_type: 需求类型（可选）
            
        Returns:
            需求列表
        """
        conditions = [
            TestRequirement.project_id == project_id,
            TestRequirement.del_flag == '0'
        ]
        
        if requirement_type:
            conditions.append(TestRequirement.requirement_type == requirement_type)
        
        query = select(TestRequirement).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    def build_query_conditions(query_params: dict) -> Select:
        """
        构建查询条件
        
        Args:
            query_params: 查询参数
            
        Returns:
            查询语句
        """
        query = select(TestRequirement).where(TestRequirement.del_flag == '0')
        
        # 需求名称模糊查询
        if requirement_name := query_params.get('requirement_name'):
            query = query.where(TestRequirement.requirement_name.like(f'%{requirement_name}%'))
        
        # 需求类型
        if requirement_type := query_params.get('requirement_type'):
            query = query.where(TestRequirement.requirement_type == requirement_type)
        
        # 项目ID
        if project_id := query_params.get('project_id'):
            query = query.where(TestRequirement.project_id == project_id)
        
        # 优先级
        if priority := query_params.get('priority'):
            query = query.where(TestRequirement.priority == priority)
        
        # 状态
        if status := query_params.get('status'):
            query = query.where(TestRequirement.status == status)
        
        # 创建者
        if create_by := query_params.get('create_by'):
            query = query.where(TestRequirement.create_by == create_by)
        
        # 排序（默认按创建时间倒序）
        query = query.order_by(TestRequirement.create_time.desc())
        
        return query
    
    @staticmethod
    async def get_requirements(
        db: AsyncSession,
        query_params: dict,
        is_page: bool = False
    ) -> dict:
        """
        获取需求列表（分页）
        
        Args:
            db: 数据库会话
            query_params: 查询参数
            is_page: 是否分页
            
        Returns:
            需求列表和总数
        """
        query = RequirementDAO.build_query_conditions(query_params)
        
        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        
        if is_page:
            page_num = query_params.get('page_num', 1)
            page_size = query_params.get('page_size', 10)
            query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        requirements = result.scalars().all()
        
        # 转换为字典列表
        rows = []
        for req in requirements:
            rows.append({
                'requirement_id': req.requirement_id,
                'project_id': req.project_id,
                'requirement_name': req.requirement_name,
                'requirement_type': req.requirement_type,
                'description': req.description,
                'acceptance_criteria': req.acceptance_criteria,
                'priority': req.priority,
                'status': req.status,
                'tags': req.tags,
                'attachments': req.attachments,
                'create_by': req.create_by,
                'create_time': req.create_time.isoformat() if req.create_time else None,
                'update_by': req.update_by,
                'update_time': req.update_time.isoformat() if req.update_time else None,
                'remark': req.remark
            })
        
        return {
            'rows': rows,
            'total': total
        }
    
    @staticmethod
    async def add_requirement(
        db: AsyncSession,
        requirement_data: dict
    ) -> TestRequirement:
        """
        创建需求
        
        Args:
            db: 数据库会话
            requirement_data: 需求数据
            
        Returns:
            创建的需求
        """
        requirement = TestRequirement(**requirement_data)
        db.add(requirement)
        await db.flush()
        await db.refresh(requirement)
        return requirement
    
    @staticmethod
    async def update_requirement(
        db: AsyncSession,
        requirement_id: int,
        requirement_data: dict
    ) -> Optional[TestRequirement]:
        """
        更新需求
        
        Args:
            db: 数据库会话
            requirement_id: 需求ID
            requirement_data: 需求数据
            
        Returns:
            更新的需求
        """
        # 先获取需求
        requirement = await RequirementDAO.get_requirement_by_id(db, requirement_id)
        if not requirement:
            return None
        
        # 更新字段
        for key, value in requirement_data.items():
            if hasattr(requirement, key) and value is not None:
                setattr(requirement, key, value)
        
        await db.flush()
        await db.refresh(requirement)
        return requirement
    
    @staticmethod
    async def delete_requirements(
        db: AsyncSession,
        requirement_ids: List[int]
    ) -> int:
        """
        删除需求（逻辑删除）
        
        Args:
            db: 数据库会话
            requirement_ids: 需求ID列表
            
        Returns:
            删除数量
        """
        query = select(TestRequirement).where(
            and_(
                TestRequirement.requirement_id.in_(requirement_ids),
                TestRequirement.del_flag == '0'
            )
        )
        result = await db.execute(query)
        requirements = result.scalars().all()
        
        for requirement in requirements:
            requirement.del_flag = '2'
        
        await db.flush()
        return len(requirements)
    
    @staticmethod
    async def count_by_project(
        db: AsyncSession,
        project_id: int,
        requirement_type: Optional[str] = None
    ) -> int:
        """
        统计项目下的需求数量
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            requirement_type: 需求类型（可选）
            
        Returns:
            需求数量
        """
        conditions = [
            TestRequirement.project_id == project_id,
            TestRequirement.del_flag == '0'
        ]
        
        if requirement_type:
            conditions.append(TestRequirement.requirement_type == requirement_type)
        
        query = select(func.count()).where(and_(*conditions))
        return await db.scalar(query) or 0
    
    @staticmethod
    async def count_by_status(
        db: AsyncSession,
        project_id: Optional[int] = None
    ) -> dict:
        """
        按状态统计需求数量
        
        Args:
            db: 数据库会话
            project_id: 项目ID（可选）
            
        Returns:
            状态统计
        """
        conditions = [TestRequirement.del_flag == '0']
        
        if project_id:
            conditions.append(TestRequirement.project_id == project_id)
        
        query = select(
            TestRequirement.status,
            func.count(TestRequirement.requirement_id).label('count')
        ).where(and_(*conditions)).group_by(TestRequirement.status)
        
        result = await db.execute(query)
        rows = result.all()
        
        status_map = {
            '0': 'pending',
            '1': 'in_progress',
            '2': 'completed',
            '3': 'closed'
        }
        
        return {
            status_map.get(row[0], 'unknown'): row[1]
            for row in rows
        }


# 别名兼容（支持旧代码引用）
RequirementDao = RequirementDAO
