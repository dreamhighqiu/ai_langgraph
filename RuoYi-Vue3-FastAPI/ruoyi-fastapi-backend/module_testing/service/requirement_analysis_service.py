"""
需求分析服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.requirement_analysis_dao import RequirementAnalysisDao
from module_testing.entity.do.requirement_analysis_do import RequirementAnalysisDO
from module_testing.entity.vo.requirement_analysis_vo import RequirementAnalysisVO, RequirementAnalysisQueryVO
from utils.log_util import logger
from utils.minio_util import MinioUtil


class RequirementAnalysisService:
    """需求分析服务"""

    def __init__(self):
        self.requirement_dao = RequirementAnalysisDao()
        self.minio_util = MinioUtil()

    async def create_requirement(
        self, 
        db: AsyncSession, 
        requirement_vo: RequirementAnalysisVO,
        user_id: int
    ) -> RequirementAnalysisDO:
        """创建需求分析"""
        try:
            # 生成需求标识符
            identifier = await self.requirement_dao.get_next_identifier(db, requirement_vo.project_id)
            
            # 创建DO对象
            requirement_do = RequirementAnalysisDO(
                project_id=requirement_vo.project_id,
                requirement_identifier=identifier,
                requirement_name=requirement_vo.requirement_name,
                requirement_type=requirement_vo.requirement_type,
                priority=requirement_vo.priority,
                status=requirement_vo.status or 'draft',
                module=requirement_vo.module,
                description=requirement_vo.description,
                acceptance_criteria=requirement_vo.acceptance_criteria,
                functional_requirements=requirement_vo.functional_requirements,
                non_functional_requirements=requirement_vo.non_functional_requirements,
                business_rules=requirement_vo.business_rules,
                dependencies=requirement_vo.dependencies,
                stakeholders=requirement_vo.stakeholders,
                created_by=user_id,
                create_time=datetime.now()
            )
            
            # 保存到数据库
            result = await self.requirement_dao.insert(db, requirement_do)
            await db.commit()
            
            logger.info(f"创建需求分析成功: {identifier}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建需求分析失败: {str(e)}")
            raise

    async def update_requirement(
        self,
        db: AsyncSession,
        requirement_id: int,
        requirement_vo: RequirementAnalysisVO,
        user_id: int
    ) -> RequirementAnalysisDO:
        """更新需求分析"""
        try:
            requirement = await self.requirement_dao.select_by_id(db, requirement_id)
            if not requirement:
                raise ValueError(f"需求分析不存在: {requirement_id}")
            
            # 更新字段
            requirement.requirement_name = requirement_vo.requirement_name
            requirement.requirement_type = requirement_vo.requirement_type
            requirement.priority = requirement_vo.priority
            requirement.status = requirement_vo.status
            requirement.module = requirement_vo.module
            requirement.description = requirement_vo.description
            requirement.acceptance_criteria = requirement_vo.acceptance_criteria
            requirement.functional_requirements = requirement_vo.functional_requirements
            requirement.non_functional_requirements = requirement_vo.non_functional_requirements
            requirement.business_rules = requirement_vo.business_rules
            requirement.dependencies = requirement_vo.dependencies
            requirement.stakeholders = requirement_vo.stakeholders
            requirement.update_time = datetime.now()
            
            result = await self.requirement_dao.update(db, requirement)
            await db.commit()
            
            logger.info(f"更新需求分析成功: {requirement_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新需求分析失败: {str(e)}")
            raise

    async def delete_requirement(self, db: AsyncSession, requirement_id: int) -> bool:
        """删除需求分析"""
        try:
            result = await self.requirement_dao.delete(db, requirement_id)
            await db.commit()
            logger.info(f"删除需求分析成功: {requirement_id}")
            return result
        except Exception as e:
            await db.rollback()
            logger.error(f"删除需求分析失败: {str(e)}")
            raise

    async def get_requirement(self, db: AsyncSession, requirement_id: int) -> Optional[RequirementAnalysisDO]:
        """获取需求分析详情"""
        return await self.requirement_dao.select_by_id(db, requirement_id)

    async def query_requirement_list(
        self,
        db: AsyncSession,
        query_vo: RequirementAnalysisQueryVO
    ) -> tuple[List[RequirementAnalysisDO], int]:
        """查询需求分析列表"""
        query_params = query_vo.dict(exclude_none=True, exclude={'page_num', 'page_size'})
        return await self.requirement_dao.select_list(
            db,
            query_params,
            query_vo.page_num,
            query_vo.page_size
        )

    async def save_to_minio(
        self,
        requirement: RequirementAnalysisDO,
        file_format: str = 'json'
    ) -> str:
        """保存需求分析到MinIO"""
        try:
            # 生成文件内容
            content = self._generate_file_content(requirement, file_format)
            
            # 上传到MinIO
            file_name = f"requirement_{requirement.requirement_identifier}.{file_format}"
            object_name = f"requirements/{requirement.project_id}/{file_name}"
            
            url = await self.minio_util.upload_file(
                bucket_name="testing",
                object_name=object_name,
                file_content=content.encode('utf-8'),
                content_type=f"application/{file_format}"
            )
            
            logger.info(f"保存需求分析到MinIO成功: {object_name}")
            return url
            
        except Exception as e:
            logger.error(f"保存需求分析到MinIO失败: {str(e)}")
            raise

    def _generate_file_content(self, requirement: RequirementAnalysisDO, file_format: str) -> str:
        """生成文件内容"""
        if file_format == 'json':
            import json
            return json.dumps({
                'requirement_identifier': requirement.requirement_identifier,
                'requirement_name': requirement.requirement_name,
                'requirement_type': requirement.requirement_type,
                'priority': requirement.priority,
                'status': requirement.status,
                'module': requirement.module,
                'description': requirement.description,
                'acceptance_criteria': requirement.acceptance_criteria,
                'functional_requirements': requirement.functional_requirements,
                'non_functional_requirements': requirement.non_functional_requirements,
                'business_rules': requirement.business_rules,
                'dependencies': requirement.dependencies,
                'stakeholders': requirement.stakeholders
            }, ensure_ascii=False, indent=2)
        else:
            # Markdown格式
            return f"""# 需求分析: {requirement.requirement_name}

**需求编号**: {requirement.requirement_identifier}
**需求类型**: {requirement.requirement_type}
**优先级**: {requirement.priority}
**状态**: {requirement.status}
**所属模块**: {requirement.module or '无'}

## 需求描述
{requirement.description or '无'}

## 验收标准
{requirement.acceptance_criteria or '无'}

## 功能需求
{requirement.functional_requirements or '无'}

## 非功能需求
{requirement.non_functional_requirements or '无'}

## 业务规则
{requirement.business_rules or '无'}

## 依赖关系
{requirement.dependencies or '无'}

## 相关干系人
{requirement.stakeholders or '无'}
"""

