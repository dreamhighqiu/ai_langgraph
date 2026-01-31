from pathlib import Path
from typing import Any, Dict, Optional

from ui_agent.automation.smart_locator_optimizer import SmartLocatorOptimizer


def ui_optimize_locators(
    url: str,
    code_path: str,
    language: str = "java",
    storage_state: Optional[str] = None,
    output_path: Optional[str] = None,
    generate_report: bool = True,
) -> Dict[str, Any]:
    """Optimize locators in existing UI automation code and generate a report."""
    code_file = Path(code_path)
    if not code_file.exists():
        raise FileNotFoundError(f"Code file not found: {code_path}")

    code = code_file.read_text(encoding="utf-8")

    if not output_path:
        output_path = str(code_file.with_suffix(code_file.suffix + ".optimized"))

    with SmartLocatorOptimizer(headless=True) as optimizer:
        optimized_code, optimizations, report_path = optimizer.optimize_code(
            code=code,
            url=url,
            language=language,
            storage_state=storage_state,
            generate_report=generate_report,
            file_path=str(code_file),
        )

    Path(output_path).write_text(optimized_code, encoding="utf-8")

    return {
        "optimized_path": output_path,
        "report_path": report_path,
        "optimized_count": len(optimizations),
    }
