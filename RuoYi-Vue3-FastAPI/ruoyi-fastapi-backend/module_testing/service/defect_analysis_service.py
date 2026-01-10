"""
缺陷分析服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
import json

from module_testing.entity.do.defect_analysis_do import DefectAnalysisDO
from module_testing.dao.defect_analysis_dao import DefectAnalysisDAO
from module_testing.service.report_template_service import get_report_template_service
from utils.log_util import logger
from utils.minio_util import MinioUtil


class DefectAnalysisService:
    """缺陷分析服务"""

    def __init__(self):
        self.dao = DefectAnalysisDAO()
        self.minio_util = MinioUtil()

    async def create_analysis(
        self,
        db: AsyncSession,
        analysis_data: dict,
        user_id: str
    ) -> DefectAnalysisDO:
        """创建缺陷分析"""
        try:
            analysis = DefectAnalysisDO(
                project_id=analysis_data.get('project_id'),
                knowledge_id=analysis_data.get('knowledge_id'),
                defect_id=analysis_data.get('defect_id'),
                analysis_name=analysis_data.get('analysis_name'),
                defect_title=analysis_data.get('defect_title'),
                defect_description=analysis_data.get('defect_description'),
                severity=analysis_data.get('severity', 'medium'),
                priority=analysis_data.get('priority', 'medium'),
                defect_type=analysis_data.get('defect_type'),
                category=analysis_data.get('category'),
                affected_phase=analysis_data.get('affected_phase'),
                detection_phase=analysis_data.get('detection_phase'),
                executive_summary=analysis_data.get('executive_summary'),
                root_cause_analysis=json.dumps(analysis_data.get('root_cause_analysis', {}), ensure_ascii=False),
                impact_analysis=json.dumps(analysis_data.get('impact_analysis', {}), ensure_ascii=False),
                reproduction_steps=json.dumps(analysis_data.get('reproduction_steps', []), ensure_ascii=False),
                affected_modules=json.dumps(analysis_data.get('affected_modules', []), ensure_ascii=False),
                fix_suggestions=json.dumps(analysis_data.get('fix_suggestions', []), ensure_ascii=False),
                test_suggestions=json.dumps(analysis_data.get('test_suggestions', []), ensure_ascii=False),
                prevention_measures=json.dumps(analysis_data.get('prevention_measures', []), ensure_ascii=False),
                similar_defects=json.dumps(analysis_data.get('similar_defects', []), ensure_ascii=False),
                use_rag=analysis_data.get('use_rag', 0),
                rag_context=analysis_data.get('rag_context'),
                mindmap_data=json.dumps(analysis_data.get('mindmap_data', {}), ensure_ascii=False),
                mindmap_url=analysis_data.get('mindmap_url'),
                status=analysis_data.get('status', 'draft'),
                process_status=analysis_data.get('process_status'),
                tags=','.join(analysis_data.get('tags', [])) if isinstance(analysis_data.get('tags'), list) else analysis_data.get('tags'),
                create_by=user_id,
                remark=analysis_data.get('remark', '')
            )
            
            return await self.dao.insert(db, analysis)
            
        except Exception as e:
            logger.error(f"创建缺陷分析失败: {str(e)}")
            raise

    async def update_analysis(
        self,
        db: AsyncSession,
        analysis_id: int,
        analysis_data: dict,
        user_id: str
    ) -> Optional[DefectAnalysisDO]:
        """更新缺陷分析"""
        try:
            analysis = await self.dao.get_by_id(db, analysis_id)
            if not analysis:
                return None
            
            # 更新字段
            for key, value in analysis_data.items():
                if key in ['root_cause_analysis', 'impact_analysis', 'reproduction_steps', 
                          'affected_modules', 'fix_suggestions', 'test_suggestions', 
                          'prevention_measures', 'similar_defects', 'mindmap_data']:
                    value = json.dumps(value, ensure_ascii=False) if value else None
                elif key == 'tags' and isinstance(value, list):
                    value = ','.join(value)
                
                if hasattr(analysis, key):
                    setattr(analysis, key, value)
            
            analysis.update_by = user_id
            analysis.update_time = datetime.now()
            
            await db.commit()
            await db.refresh(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"更新缺陷分析失败: {str(e)}")
            await db.rollback()
            raise

    async def delete_analysis(
        self,
        db: AsyncSession,
        analysis_id: int
    ) -> bool:
        """删除缺陷分析"""
        try:
            return await self.dao.delete_by_id(db, analysis_id)
        except Exception as e:
            logger.error(f"删除缺陷分析失败: {str(e)}")
            raise

    async def get_analysis(
        self,
        db: AsyncSession,
        analysis_id: int
    ) -> Optional[dict]:
        """获取缺陷分析详情"""
        try:
            analysis = await self.dao.get_by_id(db, analysis_id)
            return analysis.to_dict() if analysis else None
        except Exception as e:
            logger.error(f"获取缺陷分析详情失败: {str(e)}")
            raise

    async def query_analysis_list(
        self,
        db: AsyncSession,
        query_params: dict
    ) -> Tuple[List[dict], int]:
        """查询缺陷分析列表"""
        try:
            # 构建查询条件
            conditions = []
            
            if query_params.get('project_id'):
                conditions.append(DefectAnalysisDO.project_id == query_params['project_id'])
            if query_params.get('analysis_name'):
                conditions.append(DefectAnalysisDO.analysis_name.like(f"%{query_params['analysis_name']}%"))
            if query_params.get('severity'):
                conditions.append(DefectAnalysisDO.severity == query_params['severity'])
            if query_params.get('priority'):
                conditions.append(DefectAnalysisDO.priority == query_params['priority'])
            if query_params.get('status'):
                conditions.append(DefectAnalysisDO.status == query_params['status'])
            
            records, total = await self.dao.query_with_pagination(
                db, conditions,
                query_params.get('page_num', 1),
                query_params.get('page_size', 10)
            )
            
            return [record.to_dict() for record in records], total
            
        except Exception as e:
            logger.error(f"查询缺陷分析列表失败: {str(e)}")
            raise

    async def generate_and_upload_report(
        self,
        db: AsyncSession,
        analysis_id: int,
        template_name: Optional[str] = None
    ) -> Optional[str]:
        """
        生成缺陷分析报告并上传到MinIO，更新数据库中的report_url
        
        Args:
            db: 数据库会话
            analysis_id: 缺陷分析ID
            template_name: 模板文件名，默认为 None（使用默认模板）
        
        Returns:
            str: 报告URL，如果失败返回 None
        """
        try:
            analysis = await self.dao.get_by_id(db, analysis_id)
            if not analysis:
                logger.error(f"缺陷分析不存在: {analysis_id}")
                return None
            
            # 使用模板服务生成报告
            template_service = get_report_template_service()
            content = template_service.generate_defect_analysis_report(
                analysis,
                template_name or 'defect_analysis_report.md.jinja2'
            )
            
            # 上传到MinIO
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"defect_analysis_{analysis.analysis_id}_{timestamp}.md"
            object_name = f"defects/{analysis.project_id}/reports/{file_name}"
            
            # 直接上传文件，不生成预签名URL
            # 确保存储桶存在
            self.minio_util.create_bucket("testing")
            
            # 上传文件
            from io import BytesIO
            file_stream = BytesIO(content.encode('utf-8'))
            self.minio_util.client.put_object(
                bucket_name="testing",
                object_name=object_name,
                data=file_stream,
                length=len(content.encode('utf-8')),
                content_type="text/markdown; charset=utf-8"
            )
            
            # 更新数据库中的report_url - 存储minio://格式的路径，而不是预签名URL
            # 这样可以通过代理下载接口永久访问，不依赖预签名URL的时效性
            minio_path = f"minio://testing/{object_name}"
            analysis.report_url = minio_path
            await self.dao.update(db, analysis)
            # 注意：不在这里 commit，让调用者管理事务
            
            # 返回代理下载URL
            proxy_url = f"/testing/defect-analysis/download/{analysis_id}"
            logger.info(f"缺陷分析报告生成并上传成功: {object_name}, 代理URL: {proxy_url}")
            return proxy_url
            
        except Exception as e:
            logger.error(f"生成缺陷分析报告失败: {str(e)}", exc_info=True)
            await db.rollback()
            return None

    def _generate_report_content(self, analysis: DefectAnalysisDO) -> str:
        """
        生成缺陷分析报告内容（Markdown格式）
        
        注意：此方法已废弃，请使用 ReportTemplateService 生成报告
        保留此方法仅用于向后兼容
        """
        template_service = get_report_template_service()
        return template_service.generate_defect_analysis_report(analysis)

