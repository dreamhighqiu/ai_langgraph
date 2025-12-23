from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from ..auth import require_api_key
from ..database import get_session
from ..models import Agent, AgentRun, AgentSession
from ..schemas import RunCreate, RunOut, SessionCreate, SessionOut
from ..services.agent_runtime import run_agent
from ..services.output_storage import persist_run_output

router = APIRouter(prefix="/sessions", tags=["sessions"], dependencies=[Depends(require_api_key)])


@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate, db: Session = Depends(get_session)) -> AgentSession:
    agent = db.get(Agent, payload.agent_id)
    if not agent or not agent.is_active:
        raise HTTPException(status_code=404, detail="Agent 不存在或未启用")

    session = AgentSession(
        agent_id=payload.agent_id,
        title=payload.title or f"{agent.name} 会话",
        workspace=payload.workspace,
        meta=payload.meta,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=list[SessionOut])
def list_sessions(
    db: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    agent_id: int | None = Query(None),
) -> list[SessionOut]:
    latest_run_subq = (
        select(
            AgentRun.session_id.label("session_id"),
            func.max(AgentRun.id).label("max_run_id"),
        )
        .group_by(AgentRun.session_id)
        .subquery()
    )
    latest_run = aliased(AgentRun)
    query = (
        select(AgentSession, latest_run)
        .outerjoin(latest_run_subq, AgentSession.id == latest_run_subq.c.session_id)
        .outerjoin(latest_run, latest_run.id == latest_run_subq.c.max_run_id)
        .order_by(AgentSession.updated_at.desc())
    )
    if agent_id is not None:
        query = query.where(AgentSession.agent_id == agent_id)
    query = query.offset(offset).limit(limit)

    rows = db.execute(query).all()
    sessions: list[SessionOut] = []
    for session, last_run in rows:
        sessions.append(
            SessionOut(
                id=session.id,
                agent_id=session.agent_id,
                title=session.title,
                workspace=session.workspace,
                meta=session.meta,
                created_at=session.created_at,
                updated_at=session.updated_at,
                last_run_id=last_run.id if last_run else None,
                last_run_status=last_run.status if last_run else None,
                last_run_created_at=last_run.created_at if last_run else None,
                last_run_output_text=last_run.output_text if last_run else None,
                last_run_error=last_run.error if last_run else None,
            )
        )
    return sessions


@router.post(
    "/{session_id}/runs",
    response_model=RunOut,
    status_code=status.HTTP_201_CREATED,
)
async def execute_run(
    payload: RunCreate,
    session_id: int = Path(..., description="会话 ID"),
    db: Session = Depends(get_session),
) -> AgentRun:
    session = db.get(AgentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session 不存在")

    run = AgentRun(
        session_id=session_id,
        input_text=payload.input_text,
        status="running",
        meta=payload.meta,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        output = await run_agent(session.agent, payload.input_text)
        run.status = "succeeded"
        run.output_text = output if isinstance(output, str) else str(output)
    except Exception as exc:  # pylint: disable=broad-except
        run.status = "failed"
        run.error = str(exc)
    finally:
        session.updated_at = datetime.utcnow()
        db.add(session)
        db.add(run)
        db.commit()
        db.refresh(run)
        if run.status == "succeeded":
            persist_run_output(db, run)
            db.commit()

    return run


@router.get("/{session_id}/runs", response_model=list[RunOut])
def list_runs(session_id: int, db: Session = Depends(get_session)) -> list[AgentRun]:
    session = db.get(AgentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session 不存在")
    query = (
        select(AgentRun)
        .where(AgentRun.session_id == session_id)
        .order_by(AgentRun.created_at.desc())
    )
    return db.execute(query).scalars().all()
