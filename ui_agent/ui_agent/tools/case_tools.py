import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from ui_agent.analysis.scenario_detector import ScenarioDetector
from ui_agent.generation.ai_generator import AITestGenerator, AIConfig
from ui_agent.generation.test_case_generator import TestCaseGenerator as CaseGenerator
from ui_agent.generation.exporters import export_test_cases_excel, export_test_cases_xmind
from ui_agent.tools.common import (
    get_openai_config,
    normalize_analysis,
    default_output_dir,
    read_text,
)


def ui_generate_test_cases(
    analysis: Dict[str, Any],
    output_path: Optional[str] = None,
    use_ai: bool = False,
    reference_cases_path: Optional[str] = None,
    export_formats: Optional[Sequence[str]] = None,
    export_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate functional test cases from analysis data."""
    analysis = normalize_analysis(analysis)
    if use_ai:
        context = read_text(reference_cases_path) or ""
        try:
            openai_config = get_openai_config(api_key=api_key, model=model, base_url=base_url)
            generator = AITestGenerator(
                config=AIConfig(
                    api_key=openai_config["api_key"],
                    model=openai_config["model"],
                    base_url=openai_config["base_url"] or "https://api.openai.com/v1",
                )
            )
            cases = generator.generate_test_cases(analysis, context=context)
        except Exception as exc:
            raise RuntimeError(f"AI test case generation failed: {exc}") from exc
        summary = {"total": len(cases), "mode": "ai"}
    else:
        detector = ScenarioDetector()
        scenarios = detector.detect_from_analysis(analysis)
        case_generator = CaseGenerator()
        module_name = analysis.get("title") or analysis.get("url") or "Page"
        cases = [case.to_dict() for case in case_generator.generate_from_scenarios(scenarios, module_name)]
        summary = case_generator.get_summary()
        summary["mode"] = "rule"

    if not output_path:
        output_path = str(default_output_dir("test_cases") / "test_cases.json")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summary": summary, "cases": cases}
    output_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    exports: Dict[str, str] = {}
    if export_formats:
        base_path = Path(export_path) if export_path else output_file
        for fmt in export_formats:
            fmt_lower = fmt.lower()
            if fmt_lower == "excel":
                target = str(base_path.with_suffix(".xlsx"))
                exports["excel"] = export_test_cases_excel(payload, target)
            elif fmt_lower == "xmind":
                target = str(base_path.with_suffix(".xmind"))
                exports["xmind"] = export_test_cases_xmind(payload, target)
            elif fmt_lower == "json":
                exports["json"] = str(output_file)
            else:
                raise ValueError(f"Unsupported export format: {fmt}")

    return {
        "output_path": str(output_file),
        "summary": summary,
        "cases": cases,
        "exports": exports,
    }
