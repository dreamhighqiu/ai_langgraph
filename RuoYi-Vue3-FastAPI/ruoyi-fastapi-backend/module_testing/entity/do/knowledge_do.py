"""
知识库数据对象（DO）
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class TestKnowledge(Base):
    """知识库表"""
    __tablename__ = 'test_knowledge'
    __table_args__ = {'comment': '知识库表'}

    knowledge_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='知识库ID'
    )
    project_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='所属项目ID'
    )
    knowledge_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='知识库名称'
    )
    collection_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment='Milvus Collection 名称 (workspace)'
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='知识库描述'
    )
    file_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment='文件数量'
    )
    vector_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment='向量数量'
    )
    status: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        default='0',
        comment='状态：0正常 1停用'
    )
    create_by: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment='创建者'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        comment='创建时间'
    )
    update_by: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment='更新者'
    )
    update_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        onupdate=datetime.now,
        comment='更新时间'
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment='备注'
    )


class TestKnowledgeFile(Base):
    """知识库文件表"""
    __tablename__ = 'test_knowledge_file'
    __table_args__ = {'comment': '知识库文件表'}

    file_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='文件ID'
    )
    knowledge_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='知识库ID'
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='文件名称'
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment='MinIO存储路径'
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment='文件大小（字节）'
    )
    doc_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment='LightRAG 文档ID'
    )
    process_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='pending',
        comment='处理状态：pending/processing/completed/failed'
    )
    process_progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment='处理进度 0-100'
    )
    process_start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='处理开始时间'
    )
    process_end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='处理结束时间'
    )
    error_msg: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='错误信息'
    )
    vector_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment='生成向量数量'
    )
    create_by: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment='创建者'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        comment='创建时间'
    )
    update_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        onupdate=datetime.now,
        comment='更新时间'
    )


