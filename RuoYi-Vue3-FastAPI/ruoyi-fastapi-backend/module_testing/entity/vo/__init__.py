"""
测试模块视图对象(View Objects)
"""
from .execution_vo import (
    CancelExecutionModel,
    ExecutionDetailModel,
    ExecutionModel,
    ExecutionPageQueryModel,
)
from .project_vo import (
    AddProjectModel,
    DeleteProjectModel,
    EditProjectModel,
    ProjectModel,
    ProjectPageQueryModel,
)
from .report_vo import (
    CompareReportsModel,
    CompareReportsResponse,
    ReportDetailModel,
    ReportModel,
    ReportPageQueryModel,
)
from .script_vo import (
    AddScriptModel,
    DeleteScriptModel,
    EditScriptModel,
    ExecuteScriptModel,
    GenerateScriptModel,
    GenerateScriptResponse,
    ScriptModel,
    ScriptPageQueryModel,
)

__all__ = [
    # Project
    'ProjectModel',
    'ProjectPageQueryModel',
    'AddProjectModel',
    'EditProjectModel',
    'DeleteProjectModel',
    # Script
    'ScriptModel',
    'ScriptPageQueryModel',
    'AddScriptModel',
    'EditScriptModel',
    'DeleteScriptModel',
    'GenerateScriptModel',
    'ExecuteScriptModel',
    'GenerateScriptResponse',
    # Execution
    'ExecutionModel',
    'ExecutionPageQueryModel',
    'ExecutionDetailModel',
    'CancelExecutionModel',
    # Report
    'ReportModel',
    'ReportPageQueryModel',
    'ReportDetailModel',
    'CompareReportsModel',
    'CompareReportsResponse',
]

