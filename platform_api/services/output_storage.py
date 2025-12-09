import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from ..models import AgentOutput, AgentRun
from .persistence.requirements import persist_requirement_analysis
from .persistence.testcases import (
    persist_test_execution,
    persist_testcase_reviews,
    persist_testcases,
)


def _parse_possible_json(text: Optional[str]) -> Optional[dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        candidate = text[start : end + 1]
    else:
        candidate = text
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return None
    return None


def persist_run_output(db: Session, run: AgentRun) -> None:
    data = _parse_possible_json(run.output_text)
    summary = None
    if not data:
        summary = run.output_text[:500] if run.output_text else None
    output = AgentOutput(
        run_id=run.id,
        agent_id=run.session.agent_id,
        summary=summary,
        data=data,
    )
    db.add(output)

    agent_slug = getattr(run.session.agent, "slug", None)
    context = (run.meta or {}) | (run.session.meta or {})
    if agent_slug == "autogen_requirements_agent" and data:
        persist_requirement_analysis(db, data, context)
    elif agent_slug == "autogen_testcase_agent" and data:
        persist_testcases(db, data, context, run.id)
        persist_testcase_reviews(db, data, run.id)
    elif agent_slug == "autogen_test_execution_agent" and data:
        persist_test_execution(db, data, run.id)
