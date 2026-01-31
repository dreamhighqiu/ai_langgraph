# 使用指南（新手版）

本指南面向第一次使用 ui_agent 的同学，包含安装、配置、常用流程与排错建议。

## 1. 前置条件
- Python 3.10+
- Node.js（用于 Playwright MCP 或 Playwright 安装）
- 可访问目标站点的网络环境

## 2. 安装
```bash
pip install -r ui_agent/requirements.txt
playwright install chromium
```

## 3. 配置（只需要 3 个值）
ui_agent 只依赖以下 3 个 OpenAI 相关配置：
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`（可选）

### 方式 A：环境变量（PowerShell 示例）
```powershell
$env:OPENAI_API_KEY="your_key"
$env:OPENAI_MODEL="gpt-5.2"
$env:OPENAI_BASE_URL="https://us.api.openai.com/v1"  # 可选
```

### 方式 B：配置文件（推荐）
编辑 `ui_agent/config/config.yaml`：
```yaml
openai:
  api_key: "${OPENAI_API_KEY}"
  model: "${OPENAI_MODEL}"
  base_url: "${OPENAI_BASE_URL}"
```

> MCP 配置在 `ui_agent/config/mcp.yaml`，常用的是 `analysis.mcp.playwright_mcp` 与 `chrome_mcp`。

## 4. 登录会话（需要登录站点时）
如果目标站点需要登录，请先保存会话状态：

```bash
python -m ui_agent login --url https://harmonix-dev.zebra.com/login --output ./auth_state.json
```

若登录页加载慢，可以增加超时或调整等待策略：
```bash
python -m ui_agent login --url https://harmonix-dev.zebra.com/login --output ./auth_state.json --timeout 120000 --wait-until domcontentloaded
```

后续分析与生成时传入：
```bash
python -m ui_agent analyze --url https://harmonix-dev.zebra.com/printers/provision --auth-state ./auth_state.json --mode api
```

> MCP 模式暂不支持自动加载 `storage_state`，有登录场景请使用 `--mode api`。

## 5. 常用流程（推荐顺序）

### 5.1 页面结构分析
```bash
python -m ui_agent analyze --url https://example.com
```
- 作用：抓取页面结构与元素信息
- 输出：JSON（控制台）或使用 `--output` 写文件
 - 默认截图/分析产物保存到 `ui_agent/output/analysis_*`

### 5.2 生成功能测试用例
```bash
python -m ui_agent cases --url https://example.com --use-ai
```
- 作用：基于页面结构生成“功能测试用例”
- 默认导出：`json + excel`
- 可选导出：`xmind`

示例：
```bash
python -m ui_agent cases --url https://example.com --use-ai --format json,excel,xmind --export-path ./output/cases
```

### 5.3 生成 Java 自动化脚手架
```bash
python -m ui_agent suite --url https://example.com
```
- 作用：生成 Java PageObject + Helper + Test
- 可以传 `--reference-test` / `--reference-page` 以对齐现有代码风格

### 5.4 一键流程（分析 + 用例 + 套件）
```bash
python -m ui_agent pipeline --url https://example.com --use-ai-cases
```
- 作用：从页面分析到用例再到 Java 脚手架的完整链路
- 可加 `--mode mcp` 或 `--mode api` 强制模式

### 5.5 Chrome MCP 生成 Java 用例
```bash
python -m ui_agent chrome-suite --url https://example.com
```
- 使用 Chrome MCP 交互式理解页面并生成 Java 用例
- 配置位于 `ui_agent/config/mcp.yaml` 的 `chrome_mcp`

### 5.6 Playwright 录制脚本（codegen）
```bash
python -m ui_agent codegen --url https://example.com --language java --output ./output/recorded.java
```

### 5.7 Playwright 脚本兼容工具
```bash
python -m ui_agent script-save --file ./playwright_scripts/tests/example.spec.ts
python -m ui_agent script-run --script-path /playwright_scripts/tests/example.spec.ts
python -m ui_agent result-parse --result-path /playwright_results/result_xxx.json
```

## 6. 新手最小示例
参见：`ui_agent/docs/QUICKSTART.md`

## 7. 使用建议
- 首次使用建议从 `analyze -> cases -> suite` 按顺序跑通
- MCP 服务不可用时，使用 `--mode api` 走本地 Playwright
- 如果需要对齐项目风格，务必传入 `--reference-test` / `--reference-page`

## 8. 常见问题
- **OpenAI 报错**：检查 `OPENAI_API_KEY` 与 `OPENAI_MODEL` 是否正确
- **MCP 报错**：检查 `ui_agent/config/mcp.yaml` 中 `analysis.mcp.playwright_mcp` 或 `chrome_mcp` 配置
- **Playwright 缺失**：执行 `pip install playwright` 和 `playwright install chromium`

更多命令参数见：`ui_agent/docs/CLI_USAGE.md`
