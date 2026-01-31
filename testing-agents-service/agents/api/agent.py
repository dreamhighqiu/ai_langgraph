from pathlib import Path
from deepagents.backends import FilesystemBackend
from deepagents.middleware import SkillsMiddleware
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent as create_agent
from agents.api.tools import api_tools
from config.settings import settings
import os

# 从环境变量读取模型配置
model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
model = init_chat_model(f"openai:{model_name}")
skills_root = Path(settings.api_skills_root).resolve()
skills_backend = FilesystemBackend(root_dir=skills_root, virtual_mode=True)

workspace_root = Path(settings.api_workspace_root).resolve()
workspace_backend = FilesystemBackend(root_dir=workspace_root, virtual_mode=True)

# 创建技能中间件
skills_middleware = SkillsMiddleware(
    backend=skills_backend,
    sources=["/skills/generator/", "/skills/healer/", "/skills/planner/"]
)
agent = create_agent(
    model=model,
    tools=api_tools,
    system_prompt="""你是一位 API 自动化测试专家,掌握三个专业技能:

## 核心技能:

1. **planner** - API 测试规划
   - 从 OpenAPI/Swagger/GraphQL schema 生成全面测试计划
   - 智能生成真实测试数据
   - 设计功能、安全、边界等测试场景

2. **generator** - API 测试代码生成
   - 自动检测项目框架 (Playwright/Jest/Postman)
   - 识别编程语言 (TypeScript/JavaScript)
   - 生成可执行的测试代码

3. **healer** - API 测试修复
   - 自动诊断并修复失败的测试
   - 分析失败根因
   - 应用多种修复策略

## 工作流程:

- **需要测试计划?** → 使用 planner 技能
- **需要生成代码?** → 先用 api_project_setup 检测项目,再用 generator 生成
- **测试失败了?** → 使用 healer 技能修复

## 核心原则:

1. 仔细分析用户需求,选择最合适的技能
2. 严格按技能的工作流程执行
3. 向用户清晰说明你使用的技能和原因
4. 验证任务完成质量

通过灵活运用这三个技能,为用户提供专业的 API 测试解决方案。""",
    middleware=[skills_middleware],
    backend=workspace_backend,
)
