"""
Pytest MCP Server

Pytest 测试生成和执行服务 (Port 8004)

合并了原来的 pytest_generator (Port 8005) 和 test_executor (Port 8004)

工具列表 - 测试生成:
- generate_pytest_tests: 生成 pytest 测试文件
- generate_test_fixtures: 生成 fixtures
- generate_conftest: 生成 conftest.py

工具列表 - 测试执行:
- execute_pytest: 执行 pytest 测试（支持并行）
- generate_allure_report: 生成 Allure HTML 报告
- collect_test_results: 收集测试结果
- analyze_failures: 分析测试失败
- generate_report_summary: 生成报告摘要
- check_parallel_support: 检查并行执行支持
"""

from .server import mcp, main

__all__ = ["mcp", "main"]

