from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...legacy_models import (
    OriginalRequirementLegacy,
    ProjectLegacy,
    RequirementLegacy,
)
from ...services.minio_utils import upload_text


def _get_or_create_project(db: Session, name: Optional[str]) -> Optional[ProjectLegacy]:
    if not name:
        return None
    stmt = select(ProjectLegacy).where(ProjectLegacy.name == name)
    project = db.scalars(stmt).first()
    if project:
        return project
    project = ProjectLegacy(name=name, desc="自动创建",)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def persist_requirement_analysis(db: Session, payload: dict[str, Any], context: dict[str, Any]) -> None:
    requirements = payload.get("requirements") or []
    if not isinstance(requirements, list) or not requirements:
        return

    project_name = context.get("project_name") or context.get("project")
    project = _get_or_create_project(db, project_name)

    original_name = context.get("original_requirement_name") or context.get("title") or "AI需求分析"
    description = context.get("description") or payload.get("summary")
    report_markdown = payload.get("report") or payload.get("requirement_report")
    report_url = None
    if report_markdown:
        report_url = upload_text(report_markdown, prefix="requirement-reports")

    original_req = OriginalRequirementLegacy(
        name=original_name,
        description=description,
        status="已分析",
        project_id=project.id if project else None,
        analysis_content=payload.get("summary"),
        requirement_report=report_url,
        json_content=json.dumps(payload, ensure_ascii=False),
        review_report=json.dumps(payload.get("suggestions", []), ensure_ascii=False)
        if payload.get("suggestions")
        else None,
    )
    db.add(original_req)
    db.commit()
    db.refresh(original_req)

    for item in requirements:
        _create_requirement_record(db, original_req, project, item)


def _create_requirement_record(
    db: Session,
    original: OriginalRequirementLegacy,
    project: Optional[ProjectLegacy],
    item: dict[str, Any],
):
    name = item.get("title") or item.get("name") or "未命名需求"
    description = item.get("description") or ""
    requirement = RequirementLegacy(
        name=name,
        description=description,
        category=item.get("category"),
        module=item.get("module"),
        priority=item.get("priority"),
        project_id=project.id if project else None,
        original_requirement_id=original.id,
        original_requirement_name=original.name,
        criteria=json.dumps(item.get("acceptance_criteria", []), ensure_ascii=False),
        status="已分析",
        remark=item.get("notes"),
    )
    db.add(requirement)
