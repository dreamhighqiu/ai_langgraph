import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from ui_agent.tools.analysis_tools import ui_page_structure
from ui_agent.tools.case_tools import ui_generate_test_cases
from ui_agent.tools.suite_tools import ui_generate_test_suite
from ui_agent.tools.maintenance_tools import ui_optimize_locators
from ui_agent.tools.common import default_output_dir


def ui_full_pipeline(
    url: str,
    auth_state: Optional[str] = None,
    reference_test_path: Optional[str] = None,
    reference_page_path: Optional[str] = None,
    use_ai_cases: bool = False,
    reference_cases_path: Optional[str] = None,
    case_export_formats: Optional[Sequence[str]] = None,
    case_export_path: Optional[str] = None,
    optimize_code_path: Optional[str] = None,
    optimize_language: str = "java",
    optimize_report: bool = True,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run analysis -> test cases -> test suite generation pipeline."""
    base_dir = Path(output_dir) if output_dir else default_output_dir("ui_pipeline")

    base_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir = base_dir / "analysis"
    cases_dir = base_dir / "cases"
    suite_dir = base_dir / "suite"
    maintenance_dir = base_dir / "maintenance"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    cases_dir.mkdir(parents=True, exist_ok=True)
    suite_dir.mkdir(parents=True, exist_ok=True)
    maintenance_dir.mkdir(parents=True, exist_ok=True)

    analysis = ui_page_structure(
        url=url,
        output_dir=str(analysis_dir),
        screenshot=True,
        allow_fallback=True,
        auth_state=auth_state,
    )
    analysis_path = analysis_dir / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")

    cases_path = cases_dir / "test_cases.json"
    cases = ui_generate_test_cases(
        analysis=analysis,
        output_path=str(cases_path),
        use_ai=use_ai_cases,
        reference_cases_path=reference_cases_path,
        export_formats=case_export_formats,
        export_path=case_export_path,
    )

    suite = ui_generate_test_suite(
        url=url,
        auth_state=auth_state,
        analysis=analysis,
        reference_test_path=reference_test_path,
        reference_page_path=reference_page_path,
        output_dir=str(suite_dir),
    )

    maintenance = None
    if optimize_code_path:
        maintenance_output = maintenance_dir / (Path(optimize_code_path).name + ".optimized")
        maintenance = ui_optimize_locators(
            url=url,
            code_path=optimize_code_path,
            language=optimize_language,
            storage_state=auth_state,
            output_path=str(maintenance_output),
            generate_report=optimize_report,
        )

    return {
        "analysis_path": str(analysis_path),
        "test_cases_path": cases.get("output_path"),
        "suite_output_dir": str(suite_dir),
        "suite": suite,
        "maintenance": maintenance,
    }
