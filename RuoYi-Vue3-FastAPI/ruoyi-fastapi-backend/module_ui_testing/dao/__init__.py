"""
UI自动化测试数据访问层(DAO)
"""
from .ui_execution_dao import UIExecutionDAO
from .ui_report_dao import UIReportDAO
from .ui_script_dao import UIScriptDAO

__all__ = [
    'UIScriptDAO',
    'UIExecutionDAO',
    'UIReportDAO',
]

