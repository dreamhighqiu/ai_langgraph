from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from .database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(32), nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    graph_module = Column(String(512), nullable=False)
    graph_entrypoint = Column(String(128), nullable=False, default="agent")
    owner = Column(String(128), nullable=True)
    llm_config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    sessions = relationship("AgentSession", back_populates="agent", cascade="all, delete")


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    workspace = Column(String(128), nullable=True)
    meta = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    agent = relationship("Agent", back_populates="sessions")
    runs = relationship("AgentRun", back_populates="session", cascade="all, delete")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("agent_sessions.id"), nullable=False, index=True)
    status = Column(String(32), default="pending", nullable=False)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    meta = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    session = relationship("AgentSession", back_populates="runs")
    outputs = relationship("AgentOutput", back_populates="run", cascade="all, delete")


class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run = relationship("AgentRun", back_populates="outputs")
