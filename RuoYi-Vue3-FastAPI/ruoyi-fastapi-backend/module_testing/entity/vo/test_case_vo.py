"""
测试用例视图对象
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TestCaseStepVO(BaseModel):
    """测试步骤"""
    step_number: int = Field(..., description="步骤序号")
    action: str = Field(..., description="操作描述")
    expected: str = Field(..., description="预期结果")
    actual: Optional[str] = Field(None, description="实际结果")


class TestCaseCreateVO(BaseModel):
    """创建测试用例请求"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    case_name: str = Field(..., max_length=200, description="用例名称")
    case_type: Optional[str] = Field("functional", description="用例类型")
    template: str = Field("test_case", description="模板类型")
    description: Optional[str] = Field(None, description="用例描述")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_data: Optional[str] = Field(None, description="测试数据")
    expected_results: Optional[str] = Field(None, description="预期结果")
    test_case_steps: Optional[List[TestCaseStepVO]] = Field(None, description="测试步骤")
    feature: Optional[str] = Field(None, description="BDD Feature")
    scenario: Optional[str] = Field(None, description="BDD Scenario")
    background: Optional[str] = Field(None, description="BDD Background")
    given_steps: Optional[List[str]] = Field(None, description="BDD Given步骤")
    when_steps: Optional[List[str]] = Field(None, description="BDD When步骤")
    then_steps: Optional[List[str]] = Field(None, description="BDD Then步骤")
    priority: str = Field("medium", description="优先级")
    severity: Optional[str] = Field(None, description="严重程度")
    tags: Optional[List[str]] = Field(None, description="标签")
    remark: Optional[str] = Field(None, description="备注")


class TestCaseUpdateVO(BaseModel):
    """更新测试用例请求"""
    case_name: Optional[str] = Field(None, max_length=200, description="用例名称")
    case_type: Optional[str] = Field(None, description="用例类型")
    description: Optional[str] = Field(None, description="用例描述")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_data: Optional[str] = Field(None, description="测试数据")
    expected_results: Optional[str] = Field(None, description="预期结果")
    test_case_steps: Optional[List[TestCaseStepVO]] = Field(None, description="测试步骤")
    feature: Optional[str] = Field(None, description="BDD Feature")
    scenario: Optional[str] = Field(None, description="BDD Scenario")
    background: Optional[str] = Field(None, description="BDD Background")
    given_steps: Optional[List[str]] = Field(None, description="BDD Given步骤")
    when_steps: Optional[List[str]] = Field(None, description="BDD When步骤")
    then_steps: Optional[List[str]] = Field(None, description="BDD Then步骤")
    priority: Optional[str] = Field(None, description="优先级")
    severity: Optional[str] = Field(None, description="严重程度")
    tags: Optional[List[str]] = Field(None, description="标签")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class TestCaseQueryVO(BaseModel):
    """查询测试用例请求"""
    project_id: Optional[int] = Field(None, description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    case_name: Optional[str] = Field(None, description="用例名称(模糊查询)")
    case_type: Optional[str] = Field(None, description="用例类型")
    status: Optional[str] = Field(None, description="状态")
    priority: Optional[str] = Field(None, description="优先级")
    tags: Optional[str] = Field(None, description="标签(逗号分隔)")
    create_by: Optional[str] = Field(None, description="创建者")
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class TestCaseInfoVO(BaseModel):
    """测试用例信息"""
    case_id: int
    project_id: int
    folder_id: Optional[int]
    case_identifier: str
    case_name: str
    case_type: Optional[str]
    template: str
    description: Optional[str]
    preconditions: Optional[str]
    test_data: Optional[str]
    expected_results: Optional[str]
    test_case_steps: List[Any]
    feature: Optional[str]
    scenario: Optional[str]
    background: Optional[str]
    given_steps: List[str]
    when_steps: List[str]
    then_steps: List[str]
    priority: str
    severity: Optional[str]
    tags: List[str]
    status: str
    execution_status: Optional[str]
    execution_count: int
    pass_count: int
    fail_count: int
    create_by: str
    create_time: Optional[str]
    update_by: str
    update_time: Optional[str]
    remark: Optional[str]

    class Config:
        from_attributes = True


class TestCaseAIGenerateVO(BaseModel):
    """AI生成测试用例请求"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    requirement_text: str = Field(..., description="需求文本")
    template: str = Field("test_case", description="模板类型")
    use_rag: bool = Field(False, description="是否使用RAG")
    knowledge_id: Optional[int] = Field(None, description="知识库ID")


class TestCaseVO(BaseModel):
    """测试用例VO - 用于创建和更新"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    case_name: str = Field(..., max_length=200, description="用例名称")
    case_type: str = Field(..., description="用例类型")
    description: Optional[str] = Field(None, description="描述")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_steps: Optional[str] = Field(None, description="测试步骤")
    expected_results: Optional[str] = Field(None, description="预期结果")
    test_data: Optional[str] = Field(None, description="测试数据")
    priority: str = Field("medium", description="优先级")
    status: Optional[str] = Field("draft", description="状态")
    tags: Optional[str] = Field(None, description="标签")


class TestCaseGenerateVO(BaseModel):
    """AI生成测试用例VO"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    module_name: Optional[str] = Field(None, description="模块名称")
    feature_description: str = Field(..., description="功能描述")
    test_type: str = Field("functional", description="测试类型")
    priority: str = Field("medium", description="优先级")
    thread_id: Optional[str] = Field(None, description="会话ID")
    auto_save: bool = Field(False, description="是否自动保存")

