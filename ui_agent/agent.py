from pathlib import Path

from deepagents.backends import FilesystemBackend
from deepagents.middleware import SkillsMiddleware
from deepagents import create_deep_agent as create_agent

from ui_agent.tools import ui_tools
from ui_agent.llm import create_chat_model

llm = create_chat_model(require_api_key=False)

BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "agent_skills" / "skills"
WORKSPACE_DIR = BASE_DIR / "workspace"

skills_backend = FilesystemBackend(root_dir=SKILLS_DIR, virtual_mode=True)
workspace_backend = FilesystemBackend(root_dir=WORKSPACE_DIR, virtual_mode=True)

skills_middleware = SkillsMiddleware(
    backend=skills_backend,
    sources=[
        "/skills/analyzer/",
        "/skills/generator/",
        "/skills/maintainer/",
    ],
)

agent = create_agent(
    model=llm,
    tools=ui_tools,
    system_prompt="""
You are a UI automation agent focused on Playwright-based testing.

Core workflow:
1) Use Playwright MCP to capture page structure and element metadata.
2) Perform AI-assisted locator analysis when needed.
3) Generate functional test cases (optionally referencing existing cases).
4) Generate UI automation code (Page Object + Helper + Test) using reference project code.
5) Provide Playwright codegen recording support for custom flows.
6) Support post-generation maintenance (locator optimization and change detection).

Always prefer the MCP-based analysis tool for page structure, then reuse the output
for test case and code generation. When reference code is provided, follow its
naming and style conventions.
""",
    middleware=[skills_middleware],
    backend=workspace_backend,
)
