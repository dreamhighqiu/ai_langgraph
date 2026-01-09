"""
测试模块路由注册
"""
from fastapi import APIRouter

from module_testing.controller.test_case_controller import router as test_case_router
from module_testing.controller.bug_report_controller import router as bug_report_router
from module_testing.controller.requirement_analysis_controller import router as requirement_router
from module_testing.controller.ai_chat_controller_langgraph import router as ai_chat_router
from module_testing.controller.defect_analysis_controller import router as defect_analysis_router
from module_testing.controller.folder_controller import router as folder_router


# 创建测试模块主路由（添加 /api 前缀以匹配前端请求）
testing_router = APIRouter(prefix="/api")

# 注册各个子路由
testing_router.include_router(folder_router)  # 文件夹管理
testing_router.include_router(test_case_router)  # 测试用例管理
testing_router.include_router(bug_report_router)
testing_router.include_router(requirement_router)  # 需求分析
testing_router.include_router(ai_chat_router)  # AI 聊天接口
testing_router.include_router(defect_analysis_router)  # 缺陷分析接口

__all__ = ['testing_router']
