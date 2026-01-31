from pathlib import Path
from typing import Any, Dict, List


def _normalize_cases_payload(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict) and "cases" in payload:
        return payload.get("cases") or []
    if isinstance(payload, list):
        return payload
    return []


def export_test_cases_excel(payload: Any, output_path: str) -> str:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise RuntimeError("Missing dependency: openpyxl") from exc

    cases = _normalize_cases_payload(payload)
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"
    ws.append(
        [
            "id",
            "title",
            "priority",
            "preconditions",
            "steps",
            "expected_result",
            "locators",
        ]
    )

    for case in cases:
        preconditions = "\n".join(case.get("preconditions", []) or [])
        steps = "\n".join(case.get("steps", []) or [])
        expected = case.get("expected_result") or ""
        locators = "\n".join(case.get("locators", []) or [])
        ws.append(
            [
                case.get("id", ""),
                case.get("title", ""),
                case.get("priority", ""),
                preconditions,
                steps,
                expected,
                locators,
            ]
        )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return str(path)


def export_test_cases_xmind(payload: Any, output_path: str) -> str:
    try:
        import xmind
    except ImportError as exc:
        raise RuntimeError("Missing dependency: xmind-sdk") from exc

    cases = _normalize_cases_payload(payload)
    workbook = xmind.load(output_path)
    sheet = workbook.getPrimarySheet()
    sheet.setTitle("Test Cases")
    root = sheet.getRootTopic()
    root.setTitle("Test Cases")

    for case in cases:
        topic = root.addSubTopic()
        topic.setTitle(f"{case.get('id', '')} {case.get('title', '')}".strip())

        preconditions = case.get("preconditions", []) or []
        if preconditions:
            pre = topic.addSubTopic()
            pre.setTitle("Preconditions")
            for item in preconditions:
                pre.addSubTopic().setTitle(str(item))

        steps = case.get("steps", []) or []
        if steps:
            st = topic.addSubTopic()
            st.setTitle("Steps")
            for item in steps:
                st.addSubTopic().setTitle(str(item))

        expected = case.get("expected_result")
        if expected:
            exp = topic.addSubTopic()
            exp.setTitle("Expected")
            exp.addSubTopic().setTitle(str(expected))

    xmind.save(workbook, output_path)
    return str(Path(output_path))
