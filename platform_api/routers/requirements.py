from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..database import get_session
from ..legacy_models import OriginalRequirementLegacy, RequirementLegacy

router = APIRouter(prefix="/requirements", tags=["requirements"], dependencies=[Depends(require_api_key)])


@router.get("/original")
def list_original_requirements(db: Session = Depends(get_session)):
    stmt = select(OriginalRequirementLegacy).order_by(OriginalRequirementLegacy.created_at.desc()).limit(50)
    records = db.execute(stmt).scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "status": r.status,
            "project_id": r.project_id,
            "analysis_content": r.analysis_content,
            "requirement_report": r.requirement_report,
            "created_at": r.created_at,
        }
        for r in records
    ]


@router.get("/")
def list_requirements(db: Session = Depends(get_session)):
    stmt = select(RequirementLegacy).order_by(RequirementLegacy.created_at.desc()).limit(100)
    records = db.execute(stmt).scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "priority": r.priority,
            "status": r.status,
            "project_id": r.project_id,
            "original_requirement_id": r.original_requirement_id,
            "created_at": r.created_at,
        }
        for r in records
    ]
