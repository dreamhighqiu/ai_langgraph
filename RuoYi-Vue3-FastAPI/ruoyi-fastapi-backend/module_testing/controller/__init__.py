"""
测试模块控制器
"""
from .execution_controller import execution_controller
from .project_controller import project_controller
from .report_controller import report_controller
from .script_controller import script_controller

__all__ = [
    'project_controller',
    'script_controller',
    'execution_controller',
    'report_controller',
]

