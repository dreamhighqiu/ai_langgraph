# 架构说明

## 概览
ui_agent 的流程：
1) 页面分析（MCP 或本地 Playwright）
2) 生成功能测试用例（规则或 AI）
3) 生成 Java UI 自动化脚手架（PageObject/Helper/Test）
4) 定位器维护与优化

## 模块划分
- `ui_agent/analysis/`
  - `mcp/playwright_analyzer.py`：MCP 页面分析
  - `webpage_analyzer.py`：本地 Playwright 页面分析
  - `scenario_detector.py`：从分析结果生成场景

- `ui_agent/generation/`
  - `test_case_generator.py`：规则化功能用例生成
  - `ai_generator.py`：AI 增强用例生成

- `ui_agent/automation/`
  - `ai_page_locator_generator.py`：AI 定位器 + PageObject 生成
  - `test_case_generator.py`：Java 自动化脚手架生成
  - `smart_locator_optimizer.py`：定位器优化与验证
  - `locator_diff_reporter.py`：定位器变更报告

- `ui_agent/tools/`
  - 工具集合（analysis/cases/suite/pipeline/maintenance 等）
- `ui_agent/tools_compat.py`
  - 兼容层，保留原 `tools.py` 的统一入口
- `ui_agent/cli.py`
  - CLI 入口，提供分析/用例/套件/流水线命令

## 数据流
1) `ui_page_structure()` -> analysis payload
2) `ui_generate_test_cases()` -> cases JSON
3) `ui_generate_test_suite()` -> Java scaffolding
4) `ui_optimize_locators()` -> optimized code + report

## 设计目标
- 完全本地化，不跨项目运行依赖
- 配置驱动（模型与 MCP 不硬编码）
- 默认采用稳定定位器策略

- `ui_agent/automation/chrome_mcp_agent.py`
  - Chrome MCP 生成 Java Playwright 用例

- `ui_agent/mcp/`
  - MCP 工具注册中心（Playwright/Chrome/Chart）
