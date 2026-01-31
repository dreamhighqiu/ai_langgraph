# 最小可运行示例（Minimal Example）

本示例演示“从页面到用例到 Java 脚手架”的最小闭环。

## 1) 设置环境变量
```powershell
$env:OPENAI_API_KEY="your_key"
$env:OPENAI_MODEL="gpt-5.2"
$env:OPENAI_BASE_URL="https://us.api.openai.com/v1"  # 可选
```

## 2) （可选）保存登录会话
```bash
python -m ui_agent login --url https://harmonix-dev.zebra.com/login --output ./auth_state.json
```

## 3) 一键跑通
```bash
python -m ui_agent pipeline --url https://example.com --use-ai-cases --output-dir ./output/pipeline_demo
```

如需登录态：
```bash
python -m ui_agent pipeline --url https://harmonix-dev.zebra.com/printers/provision --use-ai-cases --auth-state ./auth_state.json --mode api
```

产物说明（示例）：
- `./output/pipeline_demo/analysis.json`
- `./output/pipeline_demo/test_cases.json`
- `./output/pipeline_demo/java`（PageObject/Helper/Test）

## 4) 分步骤跑通（可选）
```bash
# 1) 结构分析
python -m ui_agent analyze --url https://example.com --output ./output/analysis.json

# 2) 用例生成
python -m ui_agent cases --url https://example.com --use-ai --output ./output/test_cases.json --export-path ./output/cases

# 3) Java 脚手架生成
python -m ui_agent suite --url https://example.com --output-dir ./output/java_suite
```

## 5) 使用参考代码（推荐）
```bash
python -m ui_agent suite \
  --url https://example.com \
  --reference-test ./path/to/ExistingTest.java \
  --reference-page ./path/to/ExistingPage.java \
  --output-dir ./output/java_suite
```

## 6) MCP 与 API 模式切换
```bash
# 强制使用 MCP
python -m ui_agent analyze --url https://example.com --mode mcp

# 强制使用 API
python -m ui_agent analyze --url https://example.com --mode api
```
