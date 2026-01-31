# UI Generator Skill

Use when you need to generate functional test cases or UI automation code from page analysis.

Checklist:
- Prefer MCP analysis output as input for generation.
- If reference code is provided, follow its naming and locator style.
- Ensure `ui_agent/config/config.yaml` defines the OpenAI model and base URL.
- Follow `ui_agent/agent_skills/skills/generator/references/test_case_style_guide.md` for case structure and wording.
- Reference Playwright Java styles under `ui_agent/agent_skills/skills/generator/references/java/` (PageObject, Helper, Test, Hook).
- Generate functional test cases and optionally AI-enhanced cases.
- Generate Page Object + Helper + Test for Java UI automation.
- Save outputs under the workspace output directory.
