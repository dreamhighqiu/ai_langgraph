from typing import Any, Dict, Optional

from ui_agent.automation.chrome_mcp_agent import create_chrome_mcp_agent
from ui_agent.tools.common import run_async


def ui_generate_test_suite_chrome_mcp(
    url: str,
    prompt: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Use Chrome MCP agent to generate Playwright Java code."""
    agent = create_chrome_mcp_agent(debug=debug)
    user_prompt = prompt or (
        "Open the target URL, inspect the UI, and generate Playwright Java code "
        "including PageObject, Helper, and Test classes. Save the result using "
        "save_playwright_java."
    )
    result = run_async(
        agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": f"Target URL: {url}\n{user_prompt}"}
                ]
            }
        )
    )
    return {"result": result}
