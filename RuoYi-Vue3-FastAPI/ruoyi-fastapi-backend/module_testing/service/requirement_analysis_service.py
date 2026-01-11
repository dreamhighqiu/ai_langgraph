"""
需求分析服务层 (MySQL: test_requirement_analysis)
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.requirement_analysis_dao import RequirementAnalysisDao
from module_testing.entity.do.requirement_analysis_do import RequirementAnalysisDO
from module_testing.entity.vo.requirement_analysis_vo import RequirementAnalysisQueryVO, RequirementAnalysisVO
from module_testing.service.report_template_service import get_report_template_service
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
        user_id: str,
    ) -> RequirementAnalysisDO:
        """创建需求分析"""
        try:
            requirement_identifier = await self.requirement_dao.get_next_identifier(db, requirement_vo.project_id)
            requirement_do = RequirementAnalysisDO(
                project_id=requirement_vo.project_id,
                requirement_identifier=requirement_identifier,
                requirement_name=requirement_vo.requirement_name,
                requirement_type=requirement_vo.requirement_type,
                priority=requirement_vo.priority,
                status=requirement_vo.status or "draft",
                module=requirement_vo.module,
                description=requirement_vo.description,
                acceptance_criteria=requirement_vo.acceptance_criteria,
                functional_requirements=requirement_vo.functional_requirements,
                non_functional_requirements=requirement_vo.non_functional_requirements,
                business_rules=requirement_vo.business_rules,
                dependencies=requirement_vo.dependencies,
                stakeholders=requirement_vo.stakeholders,
                create_by=str(user_id),
                create_time=datetime.now(),
            )

            result = await self.requirement_dao.insert(db, requirement_do)
            await db.commit()
            logger.info(f"创建需求分析成功: {result.requirement_id}")
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
        user_id: str,
    ) -> RequirementAnalysisDO:
        """更新需求分析"""
        try:
            requirement = await self.requirement_dao.select_by_id(db, requirement_id)
            if not requirement:
                raise ValueError(f"需求分析不存在: {requirement_id}")

            requirement.requirement_name = requirement_vo.requirement_name
            requirement.requirement_type = requirement_vo.requirement_type
            requirement.priority = requirement_vo.priority
            requirement.status = requirement_vo.status or requirement.status
            requirement.module = requirement_vo.module
            requirement.description = requirement_vo.description
            requirement.acceptance_criteria = requirement_vo.acceptance_criteria
            requirement.functional_requirements = requirement_vo.functional_requirements
            requirement.non_functional_requirements = requirement_vo.non_functional_requirements
            requirement.business_rules = requirement_vo.business_rules
            requirement.dependencies = requirement_vo.dependencies
            requirement.stakeholders = requirement_vo.stakeholders
            requirement.update_by = str(user_id)
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
        query_vo: RequirementAnalysisQueryVO,
    ) -> tuple[List[RequirementAnalysisDO], int]:
        """查询需求分析列表"""
        query_params = query_vo.dict(exclude_none=True, exclude={"page_num", "page_size"})
        return await self.requirement_dao.select_list(db, query_params, query_vo.page_num, query_vo.page_size)

    async def generate_and_upload_report(
        self,
        db: AsyncSession,
        requirement_id: int,
        template_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        生成需求分析报告并上传到 MinIO；在 DB 中写入 `report_url=minio://...`；返回代理下载 URL。
        """
        try:
            requirement = await self.requirement_dao.select_by_id(db, requirement_id)
            if not requirement:
                logger.error(f"需求分析不存在: {requirement_id}")
                return None

            template_service = get_report_template_service()
            content = template_service.generate_requirement_analysis_report(
                requirement, template_name or "requirement_analysis_report.md.jinja2"
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"requirement_analysis_{requirement.requirement_id}_{timestamp}.md"
            object_name = f"requirements/{requirement.project_id}/reports/{file_name}"

            self.minio_util.create_bucket("testing")
            file_stream = BytesIO(content.encode("utf-8"))
            self.minio_util.client.put_object(
                bucket_name="testing",
                object_name=object_name,
                data=file_stream,
                length=len(content.encode("utf-8")),
                content_type="text/markdown; charset=utf-8",
            )

            requirement.report_url = f"minio://testing/{object_name}"
            await self.requirement_dao.update(db, requirement)
            await db.flush()
            # 不在这里 commit：由调用方决定事务边界

            proxy_url = f"/testing/requirement/download/{requirement_id}"
            logger.info(f"需求分析报告生成并上传成功: {object_name}, 代理URL: {proxy_url}")
            return proxy_url
        except Exception as e:
            logger.error(f"生成需求分析报告失败: {str(e)}", exc_info=True)
            await db.rollback()
            return None

    async def save_to_minio(self, requirement: RequirementAnalysisDO, file_format: str = "json") -> str:
        """保存需求分析到 MinIO（兼容旧逻辑）"""
        content = self._generate_file_content(requirement, file_format)
        file_name = f"requirement_{requirement.requirement_id}.{file_format}"
        object_name = f"requirements/{requirement.project_id}/{file_name}"
        url = await self.minio_util.upload_file(
            bucket_name="testing",
            object_name=object_name,
            file_content=content.encode("utf-8"),
            content_type=f"application/{file_format}",
        )
        logger.info(f"保存需求分析到MinIO成功: {object_name}")
        return url

    def _generate_report_content(self, requirement: RequirementAnalysisDO) -> str:
        template_service = get_report_template_service()
        return template_service.generate_requirement_analysis_report(requirement)

    def _generate_file_content(self, requirement: RequirementAnalysisDO, file_format: str) -> str:
        if file_format == "json":
            import json

            return json.dumps(
                {
                    "requirement_id": requirement.requirement_id,
                    "requirement_identifier": requirement.requirement_identifier,
                    "requirement_name": requirement.requirement_name,
                    "project_id": requirement.project_id,
                    "description": requirement.description,
                },
                ensure_ascii=False,
                indent=2,
            )
        return self._generate_report_content(requirement)

