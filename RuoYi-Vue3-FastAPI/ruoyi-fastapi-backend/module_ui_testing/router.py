"""UI自动化测试路由配置."""

from fastapi import APIRouter

# 导入controller
from module_ui_testing.controller.ui_automation_controller import ui_automation_controller

# 创建路由器
ui_testing_router = APIRouter()

# 注册子路由
ui_testing_router.include_router(ui_automation_controller)

