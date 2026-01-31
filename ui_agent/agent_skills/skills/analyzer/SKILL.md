# UI Analyzer Skill

Use when you need to capture page structure via Playwright MCP and prepare data for downstream generation.

Checklist:
- Ensure `ui_agent/config/mcp.yaml` has MCP settings for Playwright.
- Use the MCP-based page structure tool first.
- Preserve the raw element metadata for reuse.
- Follow `ui_agent/agent_skills/skills/analyzer/references/page_locator_guidelines.md` when suggesting locator strategies.
- Save analysis artifacts to the workspace output directory.
- Report missing MCP configuration if tools cannot run.
