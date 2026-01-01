"""
测试模块控制器
"""
from .agent_controller import agent_controller
from .execution_controller import execution_controller
from .health_controller import health_controller
from .knowledge_controller import knowledge_controller
from .performance_controller import performance_controller
from .project_controller import project_controller
from .report_controller import report_controller
from .requirement_controller import requirement_controller
from .script_controller import script_controller

__all__ = [
    'agent_controller',
    'execution_controller',
    'health_controller',
    'knowledge_controller',
    'performance_controller',
    'project_controller',
    'report_controller',
    'requirement_controller',
    'script_controller',
]

