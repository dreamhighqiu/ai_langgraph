"""
UI自动化测试服务层
"""
from .ui_automation_service import UIAutomationService
from .ui_execution_service import UIExecutionService
from .ui_report_service import UIReportService
from .ui_script_service import UIScriptService

__all__ = [
    'UIScriptService',
    'UIExecutionService',
    'UIReportService',
    'UIAutomationService',
]
