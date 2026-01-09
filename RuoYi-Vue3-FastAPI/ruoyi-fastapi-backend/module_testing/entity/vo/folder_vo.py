"""
文件夹视图对象
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class FolderCreateVO(BaseModel):
    """创建文件夹请求"""
    project_id: int = Field(..., description="项目ID")
    parent_id: Optional[int] = Field(None, description="父文件夹ID")
    folder_name: str = Field(..., max_length=255, description="文件夹名称")
    description: Optional[str] = Field(None, description="文件夹描述")
    sort_order: int = Field(0, description="排序顺序")
    remark: Optional[str] = Field(None, description="备注")


class FolderUpdateVO(BaseModel):
    """更新文件夹请求"""
    folder_name: Optional[str] = Field(None, max_length=255, description="文件夹名称")
    description: Optional[str] = Field(None, description="文件夹描述")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class FolderMoveVO(BaseModel):
    """移动文件夹请求"""
    folder_id: int = Field(..., description="文件夹ID")
    target_parent_id: Optional[int] = Field(None, description="目标父文件夹ID，为空表示移到根目录")


class FolderQueryVO(BaseModel):
    """查询文件夹请求"""
    project_id: Optional[int] = Field(None, description="项目ID")
    parent_id: Optional[int] = Field(None, description="父文件夹ID")
    folder_name: Optional[str] = Field(None, description="文件夹名称(模糊查询)")
    status: Optional[str] = Field(None, description="状态")
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class FolderTreeNodeVO(BaseModel):
    """文件夹树节点"""
    folder_id: int
    project_id: int
    parent_id: Optional[int]
    folder_name: str
    description: Optional[str]
    folder_path: Optional[str]
    sort_order: int
    case_count: int
    child_count: int
    status: str
    children: List['FolderTreeNodeVO'] = []
    
    class Config:
        from_attributes = True


class FolderInfoVO(BaseModel):
    """文件夹信息"""
    folder_id: int
    project_id: int
    parent_id: Optional[int]
    folder_name: str
    description: Optional[str]
    folder_path: Optional[str]
    sort_order: int
    case_count: int
    child_count: int
    status: str
    create_by: str
    create_time: Optional[str]
    update_by: str
    update_time: Optional[str]
    remark: Optional[str]
    
    class Config:
        from_attributes = True


# 更新 forward reference
FolderTreeNodeVO.model_rebuild()

