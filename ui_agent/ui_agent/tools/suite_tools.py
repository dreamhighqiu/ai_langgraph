from typing import Any, Dict, Optional

from ui_agent.automation.test_case_generator import TestCaseGenerator as SuiteGenerator
from ui_agent.tools.analysis_tools import ui_page_structure
from ui_agent.tools.common import get_openai_config, normalize_analysis, read_text, run_async, default_output_dir


def ui_generate_test_suite(
    url: str,
    auth_state: Optional[str] = None,
    analysis: Optional[Dict[str, Any]] = None,
    reference_test_path: Optional[str] = None,
    reference_page_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate Java Page Object + Helper + Test suite code."""
    openai_config = get_openai_config(api_key=api_key, model=model, base_url=base_url)

    if not analysis:
        analysis = ui_page_structure(
            url,
            screenshot=False,
            allow_fallback=True,
            auth_state=auth_state,
        )
    analysis = normalize_analysis(analysis)

    elements = analysis.get("elements", {})
    page_info = {
        "url": analysis.get("url", url),
        "title": analysis.get("title", ""),
        "html": analysis.get("html", ""),
        "buttons": elements.get("buttons", []),
        "inputs": elements.get("inputs", []),
        "forms": elements.get("forms", []),
        "tables": elements.get("tables", []),
        "links": elements.get("links", []),
    }

    reference_test = read_text(reference_test_path)
    reference_page = read_text(reference_page_path)

    generator = SuiteGenerator(
        openai_api_key=openai_config["api_key"],
        model=openai_config["model"],
        base_url=openai_config["base_url"],
    )

    test_suite = run_async(
        generator.generate_test_suite(
            url=url,
            auth_state=auth_state,
            reference_test=reference_test,
            page_object_class=reference_page,
            page_info=page_info,
        )
    )

    if not test_suite:
        raise RuntimeError("Test suite generation failed.")

    output_path = default_output_dir("test_suite")
    if output_dir:
        from pathlib import Path

        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)
    files = generator.save_to_files(test_suite, str(output_path))

    return {
        "test_class": files.get("test_class"),
        "helper_class": files.get("helper_class"),
        "json": files.get("json"),
        "test_class_name": test_suite.test_class_name,
        "helper_class_name": test_suite.helper_class_name,
        "page_object_class": test_suite.page_object_class,
        "scenarios": [s.test_method_name for s in test_suite.scenarios],
    }
