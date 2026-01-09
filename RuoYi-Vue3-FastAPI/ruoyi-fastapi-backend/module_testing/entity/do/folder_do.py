"""
文件夹数据对象
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, ForeignKey

from config.database import Base


class FolderDO(Base):
    """文件夹表"""
    __tablename__ = 'test_folder'
    __table_args__ = (
        Index('idx_folder_project_id', 'project_id'),
        Index('idx_folder_parent_id', 'parent_id'),
        Index('idx_folder_create_time', 'create_time'),
        {'comment': '测试用例文件夹表'}
    )

    # 主键
    folder_id = Column(Integer, primary_key=True, autoincrement=True, comment='文件夹ID')
    
    # 关联字段
    project_id = Column(Integer, nullable=False, comment='项目ID')
    parent_id = Column(Integer, comment='父文件夹ID，为空表示根文件夹')
    
    # 基本信息
    folder_name = Column(String(255), nullable=False, comment='文件夹名称')
    description = Column(Text, comment='文件夹描述')
    folder_path = Column(String(1000), comment='文件夹路径(用/分隔)')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    
    # 统计字段
    case_count = Column(Integer, default=0, comment='测试用例数量')
    child_count = Column(Integer, default=0, comment='子文件夹数量')
    
    # 状态字段
    status = Column(String(20), default='0', comment='状态(0正常 1停用)')
    
    # 审计字段
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), default='', comment='备注')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'folder_id': self.folder_id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'folder_name': self.folder_name,
            'description': self.description,
            'folder_path': self.folder_path,
            'sort_order': self.sort_order,
            'case_count': self.case_count,
            'child_count': self.child_count,
            'status': self.status,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'remark': self.remark
        }

