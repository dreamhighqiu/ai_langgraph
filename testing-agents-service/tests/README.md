# UI Java Agent Tests

测试 `agents/ui_java` Agent 的功能和集成。

## 运行测试

### 运行所有测试
```bash
cd testing-agents-service
pytest tests/test_ui_java_agent.py -v
```

### 运行特定测试
```bash
# 测试 Agent 创建
pytest tests/test_ui_java_agent.py::TestUIJavaAgent::test_agent_creation -v

# 测试配置加载
pytest tests/test_ui_java_agent.py::TestUIJavaAgent::test_config_loaded -v

# 测试 Planner Skill
pytest tests/test_ui_java_agent.py::TestUIJavaAgent::test_planner_skill -v
```

### 显示详细输出
```bash
pytest tests/test_ui_java_agent.py -v -s
```

### 跳过慢测试
```bash
pytest tests/test_ui_java_agent.py -v -m "not slow"
```

### 生成测试报告
```bash
# HTML 报告
pytest tests/test_ui_java_agent.py --html=report.html

# JUnit XML 报告 (CI/CD)
pytest tests/test_ui_java_agent.py --junit-xml=report.xml
```

## 测试覆盖

- ✅ Agent 创建
- ✅ 配置加载
- ✅ Skills 加载
- ✅ Planner Skill
- ✅ Generator Skill
- ✅ 错误处理
- ✅ Workspace 访问
- ✅ 完整工作流

## 前置条件

1. `.env` 文件已配置
2. 依赖已安装: `pip install -r requirements.txt`
3. pytest 已安装: `pip install pytest pytest-asyncio pytest-html`

