# ui_agent

用于页面分析、测试用例生成和 Java UI 自动化脚手架生成的工具集。

## 功能概览
- 通过 Playwright MCP 或本地 Playwright API 获取页面结构
- 生成功能测试用例（规则或 AI）
- 生成 Java PageObject + Helper + Test
- 定位器优化与变更报告
- 支持 Chrome MCP 生成 Playwright Java 用例

## 快速开始（新手建议）

1) 安装依赖
```bash
pip install -r ui_agent/requirements.txt
playwright install chromium
```

2) 配置（只需要 3 个值）
编辑 `ui_agent/config/config.yaml` 或设置环境变量：
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`（可选）

PowerShell 示例：
```powershell
$env:OPENAI_API_KEY="your_key"
$env:OPENAI_MODEL="gpt-5.2"
$env:OPENAI_BASE_URL="https://us.api.openai.com/v1"  # 可选
```

MCP 配置位于 `ui_agent/config/mcp.yaml`。

3) 登录会话（需要登录站点时）
```bash
python -m ui_agent login --url https://harmonix-dev.zebra.com/login --output ./auth_state.json
```

4) 运行示例
```bash
python -m ui_agent analyze --url https://example.com
python -m ui_agent cases --url https://example.com --use-ai
python -m ui_agent suite --url https://example.com
python -m ui_agent pipeline --url https://example.com --use-ai-cases
python -m ui_agent chrome-suite --url https://example.com
python -m ui_agent codegen --url https://example.com --language java --output ./output/recorded.java
python -m ui_agent validate
```

## 关键配置位置
- `ui_agent/config/config.yaml`：OpenAI 配置与常规配置
- `ui_agent/config/mcp.yaml`：Playwright MCP / Chrome MCP 配置

## 说明
- MCP 模式需要 `langchain-mcp-adapters` 与可用的 MCP 服务。
- 本地 API 模式需要安装 `playwright`。
- `cases` 默认导出 `json + excel`，可选 `xmind`（依赖 openpyxl 与 xmind-sdk）。
- **Headless 模式**：`ui_agent/config/config.yaml` 中 `playwright.headless` 控制，设置为 `false` 可打开浏览器窗口。
- **默认输出目录**：`analyze` 的截图与分析产物保存到 `ui_agent/output/analysis_*`。

更多教程与参数说明见：
- `ui_agent/docs/RUNBOOK.md`
- `ui_agent/docs/CLI_USAGE.md`
- `ui_agent/docs/QUICKSTART.md`
