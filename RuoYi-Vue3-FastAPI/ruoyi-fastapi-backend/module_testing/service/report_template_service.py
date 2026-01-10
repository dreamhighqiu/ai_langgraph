"""
报告模板服务

用于基于模板生成需求分析和缺陷分析报告
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from utils.log_util import logger


class ReportTemplateService:
    """报告模板服务"""
    
    def __init__(self):
        """初始化模板服务"""
        # 获取模板目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, '..', 'templates')
        
        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        logger.info(f"报告模板服务初始化完成，模板目录: {template_dir}")
    
    def generate_requirement_analysis_report(
        self,
        requirement: Any,
        template_name: str = 'requirement_analysis_report.md.jinja2'
    ) -> str:
        """
        基于模板生成需求分析报告
        
        Args:
            requirement: 需求分析对象（RequirementAnalysisDO）
            template_name: 模板文件名，默认为 'requirement_analysis_report.md.jinja2'
        
        Returns:
            str: 生成的报告内容（Markdown 格式）
        """
        try:
            # 加载模板
            template = self.env.get_template(template_name)
            
            # 解析 JSON 字段
            functional_requirements = self._parse_json_field(requirement.functional_requirements)
            non_functional_requirements = self._parse_json_field(requirement.non_functional_requirements)
            user_stories = self._parse_json_field(requirement.user_stories, default=[])
            acceptance_criteria = self._parse_json_field(requirement.acceptance_criteria)
            dependencies = self._parse_json_field(requirement.dependencies, default=[])
            risks = self._parse_json_field(requirement.risks, default=[])
            recommendations = self._parse_json_field(requirement.recommendations, default=[])
            
            # 渲染模板
            report_content = template.render(
                analysis=requirement,
                functional_requirements=functional_requirements,
                non_functional_requirements=non_functional_requirements,
                user_stories=user_stories,
                acceptance_criteria=acceptance_criteria,
                dependencies=dependencies,
                risks=risks,
                recommendations=recommendations,
                report_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            logger.info(f"需求分析报告生成成功: {requirement.analysis_id}")
            return report_content
            
        except TemplateNotFound as e:
            logger.error(f"模板文件未找到: {template_name}, 错误: {str(e)}")
            raise ValueError(f"报告模板未找到: {template_name}")
        except Exception as e:
            logger.error(f"生成需求分析报告失败: {str(e)}", exc_info=True)
            raise
    
    def generate_defect_analysis_report(
        self,
        defect: Any,
        template_name: str = 'defect_analysis_report.md.jinja2'
    ) -> str:
        """
        基于模板生成缺陷分析报告
        
        Args:
            defect: 缺陷分析对象（DefectAnalysisDO）
            template_name: 模板文件名，默认为 'defect_analysis_report.md.jinja2'
        
        Returns:
            str: 生成的报告内容（Markdown 格式）
        """
        try:
            # 加载模板
            template = self.env.get_template(template_name)
            
            # 解析 JSON 字段
            root_cause_analysis = self._parse_json_field(defect.root_cause_analysis)
            impact_analysis = self._parse_json_field(defect.impact_analysis)
            reproduction_steps = self._parse_json_field(defect.reproduction_steps, default=[])
            affected_modules = self._parse_json_field(defect.affected_modules, default=[])
            fix_suggestions = self._parse_json_field(defect.fix_suggestions, default=[])
            test_suggestions = self._parse_json_field(defect.test_suggestions, default=[])
            prevention_measures = self._parse_json_field(defect.prevention_measures, default=[])
            similar_defects = self._parse_json_field(defect.similar_defects, default=[])
            
            # 渲染模板
            report_content = template.render(
                analysis=defect,
                root_cause_analysis=root_cause_analysis,
                impact_analysis=impact_analysis,
                reproduction_steps=reproduction_steps,
                affected_modules=affected_modules,
                fix_suggestions=fix_suggestions,
                test_suggestions=test_suggestions,
                prevention_measures=prevention_measures,
                similar_defects=similar_defects,
                report_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            logger.info(f"缺陷分析报告生成成功: {defect.analysis_id}")
            return report_content
            
        except TemplateNotFound as e:
            logger.error(f"模板文件未找到: {template_name}, 错误: {str(e)}")
            raise ValueError(f"报告模板未找到: {template_name}")
        except Exception as e:
            logger.error(f"生成缺陷分析报告失败: {str(e)}", exc_info=True)
            raise
    
    def _parse_json_field(self, field_value: Optional[str], default=None):
        """
        解析 JSON 字段
        
        Args:
            field_value: JSON 字符串或 None
            default: 默认值
        
        Returns:
            解析后的对象或默认值
        """
        if not field_value:
            return default if default is not None else {}
        
        if isinstance(field_value, (dict, list)):
            return field_value
        
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"JSON 解析失败，返回原始值: {field_value}")
            return field_value
    
    def list_templates(self) -> Dict[str, list]:
        """
        列出可用的报告模板
        
        Returns:
            dict: 包含需求分析和缺陷分析模板列表的字典
        """
        try:
            template_dir = self.env.loader.searchpath[0] if self.env.loader.searchpath else None
            if not template_dir or not os.path.exists(template_dir):
                return {
                    'requirement_analysis': [],
                    'defect_analysis': []
                }
            
            templates = {
                'requirement_analysis': [],
                'defect_analysis': []
            }
            
            for filename in os.listdir(template_dir):
                if filename.endswith('.jinja2'):
                    if 'requirement' in filename.lower():
                        templates['requirement_analysis'].append(filename)
                    elif 'defect' in filename.lower():
                        templates['defect_analysis'].append(filename)
            
            return templates
            
        except Exception as e:
            logger.error(f"列出模板失败: {str(e)}", exc_info=True)
            return {
                'requirement_analysis': [],
                'defect_analysis': []
            }


# 全局单例
_template_service = None

def get_report_template_service() -> ReportTemplateService:
    """获取报告模板服务单例"""
    global _template_service
    if _template_service is None:
        _template_service = ReportTemplateService()
    return _template_service

