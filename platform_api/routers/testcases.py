from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..database import get_session
from ..legacy_models import TestCaseLegacy, TestCaseReviewLegacy, TestExecutionLegacy

router = APIRouter(prefix="/testcases", tags=["testcases"], dependencies=[Depends(require_api_key)])


@router.get("/")
def list_testcases(db: Session = Depends(get_session)):
    stmt = select(TestCaseLegacy).order_by(TestCaseLegacy.created_at.desc()).limit(100)
    records = db.execute(stmt).scalars().all()
    return [
        {
            "id": tc.id,
            "title": tc.title,
            "priority": tc.priority,
            "status": tc.status,
            "requirement_id": tc.requirement_id,
            "project_id": tc.project_id,
            "created_at": tc.created_at,
        }
        for tc in records
    ]


@router.get("/reviews")
def list_testcase_reviews(db: Session = Depends(get_session)):
    stmt = select(TestCaseReviewLegacy).order_by(TestCaseReviewLegacy.created_at.desc()).limit(50)
    records = db.execute(stmt).scalars().all()
    return [
        {
            "id": item.id,
            "test_case_id": item.test_case_id,
            "run_id": item.run_id,
            "issues": item.issues,
            "score": item.score,
            "next_steps": item.next_steps,
            "created_at": item.created_at,
        }
        for item in records
    ]


@router.get("/executions")
def list_test_executions(db: Session = Depends(get_session)):
    stmt = select(TestExecutionLegacy).order_by(TestExecutionLegacy.created_at.desc()).limit(50)
    records = db.execute(stmt).scalars().all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "status": item.status,
            "run_id": item.run_id,
            "report_url": item.report_url,
            "log_url": item.log_url,
            "created_at": item.created_at,
        }
        for item in records
    ]
