# CLI 使用说明

本文说明 `python -m ui_agent` 的命令差异、层级关系和参数用法。

## 命令关系（是否包含前置功能）
- `analyze`：只做页面分析（MCP 或本地 Playwright）。
- `cases`：先分析页面，再生成测试用例。
- `suite`：只做 Java PageObject/Helper/Test 生成，不会自动分析页面结构。
- `pipeline`：完整流程，依次执行 `analyze` -> `cases` -> `suite`，可选执行定位器优化。

包含关系说明：
- `cases` 包含 `analyze`。
- `suite` 不包含 `analyze` 与 `cases`。
- `pipeline` 包含 `analyze` + `cases` + `suite`，并可选维护阶段。

## 命令与用途

### 1) analyze
用途：获取页面结构与元素元数据，输出 JSON。

```bash
python -m ui_agent analyze --url https://example.com
```

常用参数：
- `--url`：必填，目标页面 URL
- `--mode`：可选，`mcp` 或 `api`，默认读取配置
- `--output-dir`：可选，分析产物目录
- `--output`：可选，写出 JSON 文件路径
- `--auth-state`：可选，登录态 storage_state JSON
- `--no-screenshot`：不截图
- `--no-fallback`：禁用 MCP 失败自动切换到 API

### 2) cases
用途：先分析页面，再生成结构化功能测试用例。

```bash
python -m ui_agent cases --url https://example.com --use-ai
```

常用参数：
- `--url`：必填
- `--use-ai`：使用 AI 生成用例（需要 OpenAI 配置）
- `--reference-cases`：可选，参考用例文件路径
- `--output`：可选，写出用例 JSON
- `--format`：可选，逗号分隔：`json,excel,xmind`（默认 `json,excel`）
- `--export-path`：可选，导出文件基础路径（不含扩展名）
- `--mode`：同 analyze
- `--auth-state`：可选，登录态 storage_state JSON
- `--no-screenshot`、`--no-fallback`：同 analyze

### 3) suite
用途：生成 Java PageObject/Helper/Test（不自动抓取页面）。

```bash
python -m ui_agent suite --url https://example.com
```

常用参数：
- `--url`：必填
- `--output-dir`：输出目录
- `--auth-state`：登录态文件路径
- `--reference-test`：参考 Test 类
- `--reference-page`：参考 PageObject 类

### 4) pipeline
用途：一键完整流程：分析 -> 用例 -> 套件生成，可选定位器维护。

```bash
python -m ui_agent pipeline --url https://example.com --use-ai-cases
```

常用参数：
- `--url`：必填
- `--use-ai-cases`：用 AI 生成测试用例
- `--reference-cases`：用例参考
- `--reference-test`：测试类参考
- `--reference-page`：PageObject 参考
- `--optimize-code-path`：需要优化的自动化代码路径
- `--optimize-language`：默认 `java`
- `--no-optimize-report`：不生成优化报告
- `--cases-format`：可选，逗号分隔：`json,excel,xmind`（默认 `json,excel`）
- `--cases-export-path`：可选，导出文件基础路径（不含扩展名）
- `--mode`：同 analyze
- `--auth-state`：登录态文件路径

### 5) chrome-suite
用途：使用 Chrome MCP 工具链生成 Playwright Java 自动化代码。

```bash
python -m ui_agent chrome-suite --url https://example.com
```

常用参数：
- `--url`：必填
- `--prompt`：自定义生成指令
- `--debug`：启用调试输出

### 6) codegen
用途：使用 Playwright codegen 录制脚本（可输出 Java）。

```bash
python -m ui_agent codegen --url https://example.com --language java --output ./output/recorded.java
```

### 7) script-save / script-run / result-parse
用途：保存 Playwright 脚本、执行脚本、解析结果（兼容 ui_automation 能力）。

```bash
python -m ui_agent script-save --file ./playwright_scripts/tests/example.spec.ts
python -m ui_agent script-run --script-path /playwright_scripts/tests/example.spec.ts
python -m ui_agent result-parse --result-path /playwright_results/result_xxx.json
```

### 8) login
用途：打开浏览器进行手动登录并保存会话状态（storage_state）。

```bash
python -m ui_agent login --url https://harmonix-dev.zebra.com/login --output ./auth_state.json
```

常用参数：
- `--url`：登录页
- `--output`：保存路径
- `--timeout`：导航超时（ms）
- `--wait-until`：`load` / `domcontentloaded` / `networkidle` / `commit`

## 输出说明
- `analyze`：输出页面分析 JSON（`--output` 指定）
- `cases`：默认输出 `test_cases.json` 与 Excel，可选导出 XMind
- `suite`：输出 Java PageObject/Helper/Test 文件
- `pipeline`：输出 analysis/cases/suite 目录结构，可选维护报告

## 输出路径示例
- `analyze --output ./output/analysis.json`
- `cases --output ./output/test_cases.json --export-path ./output/cases`
  - 生成：`./output/cases.json`、`./output/cases.xlsx`、`./output/cases.xmind`
- `suite --output-dir ./output/java_suite`
- `pipeline --output-dir ./output/pipeline_run`
默认情况下，`analyze` 的截图与分析文件保存到 `ui_agent/output/analysis_*`。

## 参数来源与优先级
- CLI 参数优先于 `ui_agent/config/config.yaml` 与 `ui_agent/config/mcp.yaml`
- 未指定的配置会回落到默认配置（或 `UI_AGENT_CONFIG_DIR` 指定目录）
- OpenAI 相关支持环境变量：
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
  - `OPENAI_BASE_URL`
- 模型名称：`OPENAI_MODEL` 或 `ui_agent/config/config.yaml` 中 `openai.model`
- 配置目录可由 `UI_AGENT_CONFIG_DIR` 指定

## FAQ（新手常见问题）
1) **为什么 `suite` 不会自动分析页面？**
   - `suite` 只负责生成 Java 脚手架，页面分析由 `analyze`/`cases` 完成。

2) **MCP 不可用怎么办？**
   - 使用 `--mode api` 改为本地 Playwright 分析。

3) **cases 没有生成 Excel/XMind？**
   - Excel 依赖 `openpyxl`，XMind 依赖 `xmind-sdk`。

4) **OpenAI 报错：Missing api_key/model**
   - 检查 `OPENAI_API_KEY`、`OPENAI_MODEL` 或 `ui_agent/config/config.yaml`。

5) **chrome-suite 连接失败？**
   - 检查 `ui_agent/config/mcp.yaml` 中 `chrome_mcp` 的 `url/transport`。

6) **登录态不生效？**
   - 先使用 `python -m ui_agent login` 保存 `auth_state.json`，再在 `analyze/cases/pipeline` 中传 `--auth-state`。

## 建议使用方式
- 首次接入建议使用 `pipeline`，方便端到端跑通。
- 只想拿到页面结构就用 `analyze`。
- 已有页面分析但只想出用例，用 `cases`。
- 已有参考 Test/PageObject，直接生成脚手架，用 `suite`。

## 配置目录
- 默认读取 `ui_agent/config/config.yaml` + `ui_agent/config/mcp.yaml`
- 通过 `UI_AGENT_CONFIG_DIR` 指定自定义配置目录
