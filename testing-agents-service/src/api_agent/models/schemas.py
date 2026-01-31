"""
API自动化测试系统的数据模型和类型定义

本模块定义了API测试系统中使用的所有数据结构，包括：
- API端点信息
- 测试计划和测试用例
- 测试执行结果
- 报告数据结构
"""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================

class HttpMethod(str, Enum):
    """HTTP请求方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class TestStatus(str, Enum):
    """测试执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestPriority(str, Enum):
    """测试优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(str, Enum):
    """测试类型"""
    FUNCTIONAL = "functional"
    SMOKE = "smoke"
    REGRESSION = "regression"
    PERFORMANCE = "performance"
    SECURITY = "security"
    INTEGRATION = "integration"

# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5OT1FRPT06NTI4ZGMyNDE=

# ============================================================================
# API相关模型
# ============================================================================

class APIParameter(BaseModel):
    """API参数模型"""
    name: str = Field(description="参数名称")
    param_type: str = Field(default="string", description="参数类型")
    required: bool = Field(default=False, description="是否必需")
    description: str = Field(default="", description="参数描述")
    default_value: Optional[Any] = Field(default=None, description="默认值")
    example_value: Optional[Any] = Field(default=None, description="示例值")


class APIEndpoint(BaseModel):
    """API端点模型"""
    path: str = Field(description="API路径")
    method: HttpMethod = Field(description="HTTP方法")
    summary: str = Field(default="", description="API摘要")
    description: str = Field(default="", description="API详细描述")
    tags: list[str] = Field(default_factory=list, description="API标签")
    parameters: list[APIParameter] = Field(default_factory=list, description="请求参数")
    request_body: Optional[dict[str, Any]] = Field(default=None, description="请求体Schema")
    responses: dict[str, Any] = Field(default_factory=dict, description="响应定义")
    security: list[dict[str, Any]] = Field(default_factory=list, description="安全要求")


class APISpec(BaseModel):
    """API规范模型（解析后的OpenAPI/Swagger）"""
    title: str = Field(description="API标题")
    version: str = Field(default="1.0.0", description="API版本")
    base_url: str = Field(description="API基础URL")
    description: str = Field(default="", description="API描述")
    endpoints: list[APIEndpoint] = Field(default_factory=list, description="API端点列表")
    security_schemes: dict[str, Any] = Field(default_factory=dict, description="安全方案")


# ============================================================================
# 测试用例模型
# ============================================================================
# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5OT1FRPT06NTI4ZGMyNDE=

class TestAssertion(BaseModel):
    """测试断言模型"""
    assertion_type: str = Field(description="断言类型: status_code, json_path, header, response_time等")
    expected_value: Any = Field(description="期望值")
    actual_path: Optional[str] = Field(default=None, description="实际值的JSON路径")
    operator: str = Field(default="equals", description="比较操作符: equals, contains, greater_than等")
    message: str = Field(default="", description="断言失败消息")


class TestStep(BaseModel):
    """测试步骤模型"""
    step_id: str = Field(description="步骤ID")
    name: str = Field(description="步骤名称")
    description: str = Field(default="", description="步骤描述")
    endpoint: str = Field(description="API端点路径")
    method: HttpMethod = Field(description="HTTP方法")
    headers: dict[str, str] = Field(default_factory=dict, description="请求头")
    query_params: dict[str, Any] = Field(default_factory=dict, description="查询参数")
    path_params: dict[str, Any] = Field(default_factory=dict, description="路径参数")
    request_body: Optional[Any] = Field(default=None, description="请求体")
    assertions: list[TestAssertion] = Field(default_factory=list, description="断言列表")
    extract_variables: dict[str, str] = Field(default_factory=dict, description="提取变量: {变量名: JSON路径}")
    depends_on: list[str] = Field(default_factory=list, description="依赖的步骤ID")


class TestCase(BaseModel):
    """测试用例模型"""
    case_id: str = Field(description="用例ID")
    name: str = Field(description="用例名称")
    description: str = Field(default="", description="用例描述")
    priority: TestPriority = Field(default=TestPriority.MEDIUM, description="优先级")
    test_type: TestType = Field(default=TestType.FUNCTIONAL, description="测试类型")
    tags: list[str] = Field(default_factory=list, description="标签")
    preconditions: list[str] = Field(default_factory=list, description="前置条件")
    steps: list[TestStep] = Field(default_factory=list, description="测试步骤")
    setup_steps: list[TestStep] = Field(default_factory=list, description="Setup步骤")
    teardown_steps: list[TestStep] = Field(default_factory=list, description="Teardown步骤")


class TestSuite(BaseModel):
    """测试套件模型"""
    suite_id: str = Field(description="套件ID")
    name: str = Field(description="套件名称")
    description: str = Field(default="", description="套件描述")
    base_url: str = Field(description="API基础URL")
    test_cases: list[TestCase] = Field(default_factory=list, description="测试用例列表")
    global_headers: dict[str, str] = Field(default_factory=dict, description="全局请求头")
    global_variables: dict[str, Any] = Field(default_factory=dict, description="全局变量")


# ============================================================================
# 测试计划模型
# ============================================================================

class TestPlanSection(BaseModel):
    """测试计划章节"""
    section_id: str = Field(description="章节ID")
    title: str = Field(description="章节标题")
    description: str = Field(default="", description="章节描述")
    test_cases: list[TestCase] = Field(default_factory=list, description="测试用例")


class TestPlan(BaseModel):
    """测试计划模型"""
    plan_id: str = Field(description="计划ID")
    title: str = Field(description="计划标题")
    description: str = Field(default="", description="计划描述")
    api_spec: Optional[APISpec] = Field(default=None, description="关联的API规范")
    sections: list[TestPlanSection] = Field(default_factory=list, description="测试章节")
    created_at: str = Field(default="", description="创建时间")
    updated_at: str = Field(default="", description="更新时间")


# ============================================================================
# 测试执行结果模型
# ============================================================================

class StepResult(BaseModel):
    """步骤执行结果"""
    step_id: str = Field(description="步骤ID")
    status: TestStatus = Field(description="执行状态")
    duration_ms: float = Field(default=0, description="执行耗时(毫秒)")
    request_url: str = Field(default="", description="请求URL")
    request_method: str = Field(default="", description="请求方法")
    request_headers: dict[str, str] = Field(default_factory=dict, description="请求头")
    request_body: Optional[Any] = Field(default=None, description="请求体")
    response_status: int = Field(default=0, description="响应状态码")
    response_headers: dict[str, str] = Field(default_factory=dict, description="响应头")
    response_body: Optional[Any] = Field(default=None, description="响应体")
    assertions_results: list[dict[str, Any]] = Field(default_factory=list, description="断言结果")
    extracted_variables: dict[str, Any] = Field(default_factory=dict, description="提取的变量")
    error_message: Optional[str] = Field(default=None, description="错误消息")
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5OT1FRPT06NTI4ZGMyNDE=


class CaseResult(BaseModel):
    """用例执行结果"""
    case_id: str = Field(description="用例ID")
    case_name: str = Field(description="用例名称")
    status: TestStatus = Field(description="执行状态")
    duration_ms: float = Field(default=0, description="执行耗时(毫秒)")
    step_results: list[StepResult] = Field(default_factory=list, description="步骤结果")
    error_message: Optional[str] = Field(default=None, description="错误消息")
    start_time: str = Field(default="", description="开始时间")
    end_time: str = Field(default="", description="结束时间")


class SuiteResult(BaseModel):
    """套件执行结果"""
    suite_id: str = Field(description="套件ID")
    suite_name: str = Field(description="套件名称")
    status: TestStatus = Field(description="执行状态")
    total_cases: int = Field(default=0, description="总用例数")
    passed_cases: int = Field(default=0, description="通过用例数")
    failed_cases: int = Field(default=0, description="失败用例数")
    skipped_cases: int = Field(default=0, description="跳过用例数")
    duration_ms: float = Field(default=0, description="执行耗时(毫秒)")
    case_results: list[CaseResult] = Field(default_factory=list, description="用例结果")
    start_time: str = Field(default="", description="开始时间")
    end_time: str = Field(default="", description="结束时间")


# ============================================================================
# 代码生成模型
# ============================================================================

class GeneratedTestFile(BaseModel):
    """生成的测试文件"""
    file_path: str = Field(description="文件路径")
    file_name: str = Field(description="文件名")
    content: str = Field(description="文件内容")
    language: str = Field(default="python", description="编程语言")
    framework: str = Field(default="pytest", description="测试框架")


class GenerationResult(BaseModel):
    """代码生成结果"""
    success: bool = Field(description="是否成功")
    message: str = Field(default="", description="结果消息")
    files: list[GeneratedTestFile] = Field(default_factory=list, description="生成的文件列表")
    errors: list[str] = Field(default_factory=list, description="错误列表")
    warnings: list[str] = Field(default_factory=list, description="警告列表")

# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5OT1FRPT06NTI4ZGMyNDE=

# ============================================================================
# 会话和状态模型
# ============================================================================

class AgentSession(BaseModel):
    """Agent会话模型"""
    session_id: str = Field(description="会话ID")
    api_spec: Optional[APISpec] = Field(default=None, description="API规范")
    test_plan: Optional[TestPlan] = Field(default=None, description="测试计划")
    test_suites: list[TestSuite] = Field(default_factory=list, description="测试套件")
    execution_results: list[SuiteResult] = Field(default_factory=list, description="执行结果")
    generated_files: list[GeneratedTestFile] = Field(default_factory=list, description="生成的文件")
    variables: dict[str, Any] = Field(default_factory=dict, description="会话变量")
    created_at: str = Field(default="", description="创建时间")
    updated_at: str = Field(default="", description="更新时间")

