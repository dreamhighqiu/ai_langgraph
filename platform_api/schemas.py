from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    slug: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human readable name")
    version: str = Field(default="1.0.0")
    description: Optional[str] = None
    graph_module: str = Field(..., description="Python module path \"package.module\"")
    graph_entrypoint: str = Field(default="agent", description="Callable attribute name")
    owner: Optional[str] = Field(default=None)
    llm_config: Optional[dict[str, Any]] = Field(default=None)
    is_active: bool = Field(default=True)


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    graph_module: Optional[str] = None
    graph_entrypoint: Optional[str] = None
    owner: Optional[str] = None
    llm_config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentOut(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    agent_id: int
    title: Optional[str] = None
    workspace: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class SessionCreate(SessionBase):
    pass


class SessionOut(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_run_id: Optional[int] = None
    last_run_status: Optional[str] = None
    last_run_created_at: Optional[datetime] = None
    last_run_output_text: Optional[str] = None
    last_run_error: Optional[str] = None

    class Config:
        from_attributes = True


class RunCreate(BaseModel):
    input_text: str
    meta: Optional[dict[str, Any]] = None


class RunOut(BaseModel):
    id: int
    session_id: int
    status: str
    input_text: str
    output_text: Optional[str]
    error: Optional[str]
    meta: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OutputOut(BaseModel):
    id: int
    run_id: int
    agent_id: int
    summary: Optional[str]
    data: Optional[dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
