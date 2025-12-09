import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Agent
from ..schemas import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentSimple(BaseModel):
    """简化的 Agent 信息，用于前端下拉选择"""
    id: str
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class SyncResult(BaseModel):
    """同步结果"""
    success: bool
    message: str
    imported: int = 0
    skipped: int = 0


# Agent 显示名称映射
AGENT_DISPLAY_NAMES = {
    "performance_agent": "🚀 性能测试智能体",
    "research_agent": "🔍 研究智能体",
    "interrupt_agent": "⏸️ 中断智能体",
    "knowledge_agent": "📚 知识库智能体",
    "web_scraper_agent": "🌐 网页抓取智能体",
}


@router.get("/simple", response_model=list[AgentSimple])
def list_agents_simple(session: Session = Depends(get_session)) -> list[dict]:
    """获取简化的 Agent 列表，用于前端下拉选择"""
    agents = session.execute(
        select(Agent).where(Agent.is_active == True).order_by(Agent.slug)
    ).scalars().all()
    
    return [
        {
            "id": agent.slug,
            "name": AGENT_DISPLAY_NAMES.get(agent.slug, agent.name),
            "description": agent.description,
        }
        for agent in agents
    ]


@router.post("/sync", response_model=SyncResult)
def sync_from_graph_json(
    graph_path: str = "testing-deep-agents-service/graph.json",
    session: Session = Depends(get_session),
) -> SyncResult:
    """从 graph.json 同步 Agent 配置到数据库"""
    try:
        path = Path(graph_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {graph_path}")
        
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        
        graphs = data.get("graphs", {})
        imported = 0
        skipped = 0
        
        for slug, payload in graphs.items():
            # 解析模块路径
            module_path, entrypoint = (
                payload.get("path", "").split(":", maxsplit=1) + ["agent"]
            )[:2]
            module_path = module_path.strip("./")
            if module_path.startswith("src/"):
                module_path = module_path[4:]
            if module_path.endswith(".py"):
                module_path = module_path[:-3]
            module_path = module_path.replace("/", ".")
            entrypoint = entrypoint or "agent"
            
            # 检查是否已存在
            exists = session.execute(
                select(Agent).where(Agent.slug == slug)
            ).scalar_one_or_none()
            
            if exists:
                # 更新现有记录
                exists.graph_module = module_path
                exists.graph_entrypoint = entrypoint
                exists.name = AGENT_DISPLAY_NAMES.get(slug, slug)
                skipped += 1
            else:
                # 创建新记录
                agent = Agent(
                    slug=slug,
                    name=AGENT_DISPLAY_NAMES.get(slug, slug),
                    description=f"从 graph.json 导入的智能体",
                    graph_module=module_path,
                    graph_entrypoint=entrypoint,
                    owner="system",
                )
                session.add(agent)
                imported += 1
        
        session.commit()
        
        return SyncResult(
            success=True,
            message=f"同步完成: 新增 {imported} 个，更新 {skipped} 个",
            imported=imported,
            skipped=skipped,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[AgentOut])
def list_agents(session: Session = Depends(get_session)) -> list[Agent]:
    agents = session.execute(select(Agent).order_by(Agent.slug)).scalars().all()
    return agents


@router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
def create_agent(payload: AgentCreate, session: Session = Depends(get_session)) -> Agent:
    existing = session.execute(select(Agent).where(Agent.slug == payload.slug)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Agent slug already exists")

    agent = Agent(**payload.model_dump())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


@router.get("/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: int, session: Session = Depends(get_session)) -> Agent:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=AgentOut)
def update_agent(
    agent_id: int,
    payload: AgentUpdate,
    session: Session = Depends(get_session),
) -> Agent:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agent, key, value)

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, session: Session = Depends(get_session)) -> None:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    session.delete(agent)
    session.commit()
