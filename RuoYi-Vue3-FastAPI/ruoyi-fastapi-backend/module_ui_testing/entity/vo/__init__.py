"""
UI自动化测试视图对象(View Objects)
"""
from .ui_execution_vo import (
    CancelUIExecutionModel,
    UIExecutionDetailModel,
    UIExecutionModel,
    UIExecutionPageQueryModel,
)
from .ui_report_vo import (
    CompareUIReportsModel,
    CompareUIReportsResponse,
    UIReportDetailModel,
    UIReportModel,
    UIReportPageQueryModel,
)
from .ui_script_vo import (
    AddUIScriptModel,
    DeleteUIScriptModel,
    EditUIScriptModel,
    ExecuteUIScriptModel,
    GenerateUIScriptModel,
    GenerateUIScriptResponse,
    UIScriptExecuteRequest,
    UIScriptGenerateRequest,
    UIScriptModel,
    UIScriptPageQueryModel,
)

__all__ = [
    # UI Script
    'UIScriptModel',
    'UIScriptPageQueryModel',
    'AddUIScriptModel',
    'EditUIScriptModel',
    'DeleteUIScriptModel',
    'GenerateUIScriptModel',
    'ExecuteUIScriptModel',
    'GenerateUIScriptResponse',
    'UIScriptGenerateRequest',  # 别名
    'UIScriptExecuteRequest',   # 别名
    # UI Execution
    'UIExecutionModel',
    'UIExecutionPageQueryModel',
    'UIExecutionDetailModel',
    'CancelUIExecutionModel',
    # UI Report
    'UIReportModel',
    'UIReportPageQueryModel',
    'UIReportDetailModel',
    'CompareUIReportsModel',
    'CompareUIReportsResponse',
]
