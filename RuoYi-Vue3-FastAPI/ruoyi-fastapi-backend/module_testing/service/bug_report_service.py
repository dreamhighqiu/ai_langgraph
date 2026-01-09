"""
缺陷报告服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.bug_report_dao import BugReportDao
from module_testing.entity.do.bug_report_do import BugReportDO
from module_testing.entity.vo.bug_report_vo import BugReportVO, BugReportQueryVO
from utils.log_util import logger
from utils.minio_util import MinioUtil


class BugReportService:
    """缺陷报告服务"""

    def __init__(self):
        self.bug_report_dao = BugReportDao()
        self.minio_util = MinioUtil()

    async def create_bug_report(
        self, 
        db: AsyncSession, 
        bug_report_vo: BugReportVO,
        user_id: int
    ) -> BugReportDO:
        """创建缺陷报告"""
        try:
            # 生成缺陷标识符
            identifier = await self.bug_report_dao.get_next_identifier(db, bug_report_vo.project_id)
            
            # 创建DO对象
            bug_report_do = BugReportDO(
                project_id=bug_report_vo.project_id,
                bug_identifier=identifier,
                bug_title=bug_report_vo.bug_title,
                bug_description=bug_report_vo.bug_description,
                severity=bug_report_vo.severity,
                priority=bug_report_vo.priority,
                bug_type=bug_report_vo.bug_type,
                status=bug_report_vo.status or 'open',
                environment=bug_report_vo.environment,
                steps_to_reproduce=bug_report_vo.steps_to_reproduce,
                expected_behavior=bug_report_vo.expected_behavior,
                actual_behavior=bug_report_vo.actual_behavior,
                attachments=bug_report_vo.attachments,
                reporter=user_id,
                assigned_to=bug_report_vo.assigned_to,
                create_time=datetime.now()
            )
            
            # 保存到数据库
            result = await self.bug_report_dao.insert(db, bug_report_do)
            await db.commit()
            
            logger.info(f"创建缺陷报告成功: {identifier}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建缺陷报告失败: {str(e)}")
            raise

    async def update_bug_report(
        self,
        db: AsyncSession,
        bug_id: int,
        bug_report_vo: BugReportVO,
        user_id: int
    ) -> BugReportDO:
        """更新缺陷报告"""
        try:
            bug_report = await self.bug_report_dao.select_by_id(db, bug_id)
            if not bug_report:
                raise ValueError(f"缺陷报告不存在: {bug_id}")
            
            # 更新字段
            bug_report.bug_title = bug_report_vo.bug_title
            bug_report.bug_description = bug_report_vo.bug_description
            bug_report.severity = bug_report_vo.severity
            bug_report.priority = bug_report_vo.priority
            bug_report.bug_type = bug_report_vo.bug_type
            bug_report.status = bug_report_vo.status
            bug_report.environment = bug_report_vo.environment
            bug_report.steps_to_reproduce = bug_report_vo.steps_to_reproduce
            bug_report.expected_behavior = bug_report_vo.expected_behavior
            bug_report.actual_behavior = bug_report_vo.actual_behavior
            bug_report.attachments = bug_report_vo.attachments
            bug_report.assigned_to = bug_report_vo.assigned_to
            bug_report.update_time = datetime.now()
            
            result = await self.bug_report_dao.update(db, bug_report)
            await db.commit()
            
            logger.info(f"更新缺陷报告成功: {bug_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新缺陷报告失败: {str(e)}")
            raise

    async def delete_bug_report(self, db: AsyncSession, bug_id: int) -> bool:
        """删除缺陷报告"""
        try:
            result = await self.bug_report_dao.delete(db, bug_id)
            await db.commit()
            logger.info(f"删除缺陷报告成功: {bug_id}")
            return result
        except Exception as e:
            await db.rollback()
            logger.error(f"删除缺陷报告失败: {str(e)}")
            raise

    async def get_bug_report(self, db: AsyncSession, bug_id: int) -> Optional[BugReportDO]:
        """获取缺陷报告详情"""
        return await self.bug_report_dao.select_by_id(db, bug_id)

    async def query_bug_report_list(
        self,
        db: AsyncSession,
        query_vo: BugReportQueryVO
    ) -> tuple[List[BugReportDO], int]:
        """查询缺陷报告列表"""
        query_params = query_vo.dict(exclude_none=True, exclude={'page_num', 'page_size'})
        return await self.bug_report_dao.select_list(
            db,
            query_params,
            query_vo.page_num,
            query_vo.page_size
        )

    async def save_to_minio(
        self,
        bug_report: BugReportDO,
        file_format: str = 'json'
    ) -> str:
        """保存缺陷报告到MinIO"""
        try:
            # 生成文件内容
            content = self._generate_file_content(bug_report, file_format)
            
            # 上传到MinIO
            file_name = f"bug_report_{bug_report.bug_identifier}.{file_format}"
            object_name = f"bug-reports/{bug_report.project_id}/{file_name}"
            
            url = await self.minio_util.upload_file(
                bucket_name="testing",
                object_name=object_name,
                file_content=content.encode('utf-8'),
                content_type=f"application/{file_format}"
            )
            
            logger.info(f"保存缺陷报告到MinIO成功: {object_name}")
            return url
            
        except Exception as e:
            logger.error(f"保存缺陷报告到MinIO失败: {str(e)}")
            raise

    def _generate_file_content(self, bug_report: BugReportDO, file_format: str) -> str:
        """生成文件内容"""
        if file_format == 'json':
            import json
            return json.dumps({
                'bug_identifier': bug_report.bug_identifier,
                'bug_title': bug_report.bug_title,
                'bug_description': bug_report.bug_description,
                'severity': bug_report.severity,
                'priority': bug_report.priority,
                'bug_type': bug_report.bug_type,
                'status': bug_report.status,
                'environment': bug_report.environment,
                'steps_to_reproduce': bug_report.steps_to_reproduce,
                'expected_behavior': bug_report.expected_behavior,
                'actual_behavior': bug_report.actual_behavior
            }, ensure_ascii=False, indent=2)
        else:
            # Markdown格式
            return f"""# 缺陷报告: {bug_report.bug_title}

**缺陷编号**: {bug_report.bug_identifier}
**严重程度**: {bug_report.severity}
**优先级**: {bug_report.priority}
**缺陷类型**: {bug_report.bug_type}
**状态**: {bug_report.status}

## 环境信息
{bug_report.environment or '无'}

## 问题描述
{bug_report.bug_description or '无'}

## 复现步骤
{bug_report.steps_to_reproduce or '无'}

## 预期行为
{bug_report.expected_behavior or '无'}

## 实际行为
{bug_report.actual_behavior or '无'}
"""

