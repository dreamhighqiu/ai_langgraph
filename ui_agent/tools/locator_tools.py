from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from ui_agent.automation.ai_page_locator_generator import AIPageLocatorGenerator
from ui_agent.tools.common import get_openai_config, read_text, default_output_dir, run_async


def ui_ai_locator_analysis(
    url: str,
    output_dir: Optional[str] = None,
    auth_state: Optional[str] = None,
    reference_code_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Run AI locator analysis and generate a Java Page Object."""
    openai_config = get_openai_config(api_key=api_key, model=model, base_url=base_url)

    reference_code = read_text(reference_code_path)
    generator = AIPageLocatorGenerator(
        openai_api_key=openai_config["api_key"],
        model=openai_config["model"],
        base_url=openai_config["base_url"],
    )

    analysis = run_async(
        generator.analyze_page_with_browser_use(
            url=url,
            auth_state=auth_state,
            reference_code=reference_code,
        )
    )

    if not analysis:
        raise RuntimeError("AI locator analysis failed.")

    output_path = Path(output_dir) if output_dir else default_output_dir("ai_locators")
    output_path.mkdir(parents=True, exist_ok=True)
    java_path = generator.save_to_file(analysis, str(output_path))

    return {
        "page_url": analysis.page_url,
        "page_title": analysis.page_title,
        "class_name": analysis.class_name,
        "package_name": analysis.package_name,
        "timestamp": analysis.timestamp,
        "java_path": java_path,
        "analysis": asdict(analysis),
    }
