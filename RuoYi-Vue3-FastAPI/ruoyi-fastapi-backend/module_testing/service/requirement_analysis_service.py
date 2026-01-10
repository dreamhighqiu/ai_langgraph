"""
需求分析服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.requirement_analysis_dao import RequirementAnalysisDao
from module_testing.entity.do.requirement_analysis_do import RequirementAnalysisDO
from module_testing.entity.vo.requirement_analysis_vo import RequirementAnalysisVO, RequirementAnalysisQueryVO
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
        user_id: str
    ) -> RequirementAnalysisDO:
        """创建需求分析"""
        try:
            # 创建DO对象 - 使用正确的字段名
            requirement_do = RequirementAnalysisDO(
                project_id=requirement_vo.project_id,
                analysis_name=requirement_vo.requirement_name,  # 映射到 analysis_name
                executive_summary=requirement_vo.description,  # 描述映射到 executive_summary
                functional_requirements=requirement_vo.functional_requirements,
                non_functional_requirements=requirement_vo.non_functional_requirements,
                acceptance_criteria=requirement_vo.acceptance_criteria,
                dependencies=requirement_vo.dependencies,
                status=requirement_vo.status or 'draft',
                create_by=str(user_id),  # 使用 create_by 而不是 created_by
                create_time=datetime.now()
            )
            
            # 保存到数据库
            result = await self.requirement_dao.insert(db, requirement_do)
            await db.commit()
            
            logger.info(f"创建需求分析成功: {result.analysis_id}")
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
        user_id: str
    ) -> RequirementAnalysisDO:
        """更新需求分析"""
        try:
            requirement = await self.requirement_dao.select_by_id(db, requirement_id)
            if not requirement:
                raise ValueError(f"需求分析不存在: {requirement_id}")
            
            # 更新字段 - 使用正确的字段名
            requirement.analysis_name = requirement_vo.requirement_name  # 映射到 analysis_name
            requirement.executive_summary = requirement_vo.description  # 描述映射到 executive_summary
            requirement.status = requirement_vo.status or requirement.status
            requirement.acceptance_criteria = requirement_vo.acceptance_criteria
            requirement.functional_requirements = requirement_vo.functional_requirements
            requirement.non_functional_requirements = requirement_vo.non_functional_requirements
            requirement.dependencies = requirement_vo.dependencies
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

    async def generate_and_upload_report(
        self,
        db: AsyncSession,
        analysis_id: int,
        template_name: Optional[str] = None
    ) -> Optional[str]:
        """
        生成需求分析报告并上传到MinIO，更新数据库中的report_url
        
        Args:
            db: 数据库会话
            analysis_id: 需求分析ID (analysis_id)
            template_name: 模板文件名，默认为 None（使用默认模板）
        
        Returns:
            str: 报告URL，如果失败返回 None
        """
        try:
            requirement = await self.requirement_dao.select_by_id(db, analysis_id)
            if not requirement:
                logger.error(f"需求分析不存在: {analysis_id}")
                return None
            
            # 使用模板服务生成报告
            template_service = get_report_template_service()
            content = template_service.generate_requirement_analysis_report(
                requirement,
                template_name or 'requirement_analysis_report.md.jinja2'
            )
            
            # 上传到MinIO
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"requirement_analysis_{requirement.analysis_id}_{timestamp}.md"
            object_name = f"requirements/{requirement.project_id}/reports/{file_name}"
            
            url = await self.minio_util.upload_file(
                bucket_name="testing",
                object_name=object_name,
                file_content=content.encode('utf-8'),
                content_type="text/markdown; charset=utf-8"
            )
            
            # 更新数据库中的report_url
            requirement.report_url = url
            await self.requirement_dao.update(db, requirement)
            await db.commit()
            
            logger.info(f"需求分析报告生成并上传成功: {object_name}, URL: {url}")
            return url
            
        except Exception as e:
            logger.error(f"生成需求分析报告失败: {str(e)}", exc_info=True)
            await db.rollback()
            return None

    async def save_to_minio(
        self,
        requirement: RequirementAnalysisDO,
        file_format: str = 'json'
    ) -> str:
        """保存需求分析到MinIO（保留旧方法以兼容）"""
        try:
            # 生成文件内容
            content = self._generate_file_content(requirement, file_format)
            
            # 上传到MinIO
            file_name = f"requirement_{requirement.analysis_id}.{file_format}"
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

    def _generate_report_content(self, requirement: RequirementAnalysisDO) -> str:
        """
        生成需求分析报告内容（Markdown格式）
        
        注意：此方法已废弃，请使用 ReportTemplateService 生成报告
        保留此方法仅用于向后兼容
        """
        template_service = get_report_template_service()
        return template_service.generate_requirement_analysis_report(requirement)

    def _generate_file_content(self, requirement: RequirementAnalysisDO, file_format: str) -> str:
        """生成文件内容（保留旧方法以兼容）"""
        if file_format == 'json':
            import json
            return json.dumps({
                'analysis_id': requirement.analysis_id,
                'analysis_name': requirement.analysis_name,
                'project_id': requirement.project_id,
                'executive_summary': requirement.executive_summary,
            }, ensure_ascii=False, indent=2)
        else:
            # 使用新的报告生成方法
            return self._generate_report_content(requirement)

