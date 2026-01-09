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
from utils.log_util import logger


class DefectAnalysisService:
    """缺陷分析服务"""

    def __init__(self):
        self.dao = DefectAnalysisDAO()

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

