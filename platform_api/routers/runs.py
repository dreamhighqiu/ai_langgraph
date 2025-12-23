from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..database import get_session
from ..models import AgentOutput, AgentRun
from ..schemas import OutputOut

router = APIRouter(
    prefix="/runs",
    tags=["runs"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/{run_id}/outputs", response_model=list[OutputOut])
def list_run_outputs(
    run_id: int = Path(..., description="运行 ID"),
    db: Session = Depends(get_session),
):
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run 不存在")
    outputs = (
        db.query(AgentOutput)
        .filter(AgentOutput.run_id == run_id)
        .order_by(AgentOutput.created_at.asc())
        .all()
    )
    return outputs
