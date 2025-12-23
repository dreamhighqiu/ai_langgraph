from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from ...legacy_models import (
    ReportLegacy,
    TestCaseLegacy,
    TestCaseReviewLegacy,
    TestExecutionLegacy,
    TestStepLegacy,
)
from ...services.minio_utils import upload_text


def persist_testcases(db: Session, payload: dict[str, Any], context: dict[str, Any], run_id: int) -> None:
    testcases = payload.get("testcases") or []
    if not isinstance(testcases, list):
        return
    requirement_id = context.get("requirement_id") or context.get("requirement")
    project_id = context.get("project_id")

    for tc in testcases:
        _create_testcase(db, tc, requirement_id, project_id, run_id)


def _create_testcase(db: Session, data: dict[str, Any], requirement_id: int | None, project_id: int | None, run_id: int) -> None:
    title = data.get("title") or "自动生成测试用例"
    test_case = TestCaseLegacy(
        title=title,
        desc=data.get("objective") or data.get("description"),
        priority=data.get("priority"),
        status="待执行",
        tags=",".join(data.get("tags", [])) or None,
        preconditions="\n".join(data.get("preconditions", [])) or None,
        postconditions="\n".join(data.get("postconditions", [])) or None,
        requirement_id=requirement_id or data.get("requirement_id"),
        project_id=project_id,
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)

    steps = data.get("steps", [])
    expected = data.get("expected_results", [])
    for idx, step in enumerate(steps):
        exp = expected[idx] if idx < len(expected) else None
        step_record = TestStepLegacy(
            test_case_id=test_case.id,
            description=step,
            expected_result=exp,
            order=idx,
        )
        db.add(step_record)
    db.commit()


def persist_testcase_reviews(db: Session, payload: dict[str, Any], run_id: int) -> None:
    reviews = payload.get("review")
    if not reviews:
        return
    review_record = TestCaseReviewLegacy(
        run_id=run_id,
        issues=reviews,
        score=payload.get("score"),
        next_steps=payload.get("next_steps"),
    )
    db.add(review_record)


def persist_test_execution(db: Session, payload: dict[str, Any], run_id: int) -> None:
    report_text = payload.get("report_markdown") or payload.get("markdown")
    report_url = None
    if report_text:
        report_url = upload_text(report_text, prefix="test-execution-reports")

    execution = TestExecutionLegacy(
        run_id=run_id,
        name=payload.get("name") or payload.get("plan") or "自动化执行",
        status=payload.get("status") or "unknown",
        result=json.dumps(payload.get("result"), ensure_ascii=False)
        if isinstance(payload.get("result"), (dict, list))
        else payload.get("result"),
        report_url=report_url,
        log_url=payload.get("log_url"),
        metadata_payload=payload,
    )
    db.add(execution)

    if report_url:
        report = ReportLegacy(
            run_id=run_id,
            title=payload.get("name") or "测试执行报告",
            summary=payload.get("summary"),
            url=report_url,
            type="test_execution",
        )
        db.add(report)
