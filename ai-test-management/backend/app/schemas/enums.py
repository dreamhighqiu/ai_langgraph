"""
系统枚举值定义

基于 BrowserStack Test Management API 的枚举值定义
参考: https://www.browserstack.com/docs/test-management/api-reference/enums
"""



from enum import Enum


class Priority(str, Enum):
    """
    测试用例优先级
    
    用于标识测试用例的重要程度和执行优先顺序
    """
    LOW = "low"           # 低优先级
    MEDIUM = "medium"     # 中优先级
    HIGH = "high"         # 高优先级
    CRITICAL = "critical" # 关键优先级


class TestCaseState(str, Enum):
    """
    测试用例状态
    
    用于标识测试用例在生命周期中的当前状态
    """
    ACTIVE = "active"         # 活跃状态 - 可以执行
    DRAFT = "draft"           # 草稿状态 - 正在编写
    IN_REVIEW = "in_review"   # 审核中 - 等待审批
    REJECTED = "rejected"     # 已拒绝 - 审核未通过
    OUTDATED = "outdated"     # 已过时 - 需要更新


class TestCaseType(str, Enum):
    """
    测试用例类型
    
    用于分类测试用例的测试类型
    """
    ACCEPTANCE = "acceptance"       # 验收测试
    ACCESSIBILITY = "accessibility" # 可访问性测试
    COMPATIBILITY = "compatibility" # 兼容性测试
    DESTRUCTIVE = "destructive"     # 破坏性测试
    FUNCTIONAL = "functional"       # 功能测试
    OTHER = "other"                 # 其他类型
    PERFORMANCE = "performance"     # 性能测试
    REGRESSION = "regression"       # 回归测试
    SECURITY = "security"           # 安全测试
    SMOKE_SANITY = "smoke_sanity"   # 冒烟和健全性测试
    USABILITY = "usability"         # 可用性测试
# pragma: no cover  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUdaa1R3PT06MjViNmVhMGY=


class HTTPStatusCode(int, Enum):
    """
    HTTP 状态码
    
    API 响应使用的标准 HTTP 状态码
    参考: https://www.browserstack.com/docs/test-management/api-reference/status-code
    """
    OK = 200                    # 请求成功
    CREATED = 201               # 资源创建成功
    NO_CONTENT = 204            # 无内容（删除成功）
    BAD_REQUEST = 400           # 请求格式错误
    UNAUTHORIZED = 401          # 未授权 - 无效的访问凭证
    FORBIDDEN = 403             # 禁止访问
    NOT_FOUND = 404             # 资源未找到
    UNPROCESSABLE_ENTITY = 422  # 请求格式正确但语义错误
    TOO_MANY_REQUESTS = 429     # 请求过多 - 超出速率限制
    INTERNAL_SERVER_ERROR = 500 # 服务器内部错误


class SortOrder(str, Enum):
    """排序顺序"""
    ASC = "asc"   # 升序
    DESC = "desc" # 降序


class IssueType(str, Enum):
    """
    关联问题类型

    用于标识测试用例关联的外部问题类型
    """
    JIRA = "jira"           # Jira 问题
    GITHUB = "github"       # GitHub Issue
    GITLAB = "gitlab"       # GitLab Issue
    AZURE = "azure"         # Azure DevOps
    OTHER = "other"         # 其他类型

# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUdaa1R3PT06MjViNmVhMGY=

class TestCaseTemplate(str, Enum):
    """
    测试用例模板类型

    用于区分普通测试用例和 BDD 测试用例
    """
    TEST_CASE = "test_case"       # 普通测试用例
    TEST_CASE_BDD = "test_case_bdd"  # BDD 测试用例


class AutomationStatus(str, Enum):
    """
    自动化状态

    用于标识测试用例的自动化程度
    """
    NOT_AUTOMATED = "not_automated"   # 未自动化
    AUTOMATED = "automated"           # 已自动化
    IN_PROGRESS = "in_progress"       # 自动化进行中
    OBSOLETE = "obsolete"             # 自动化已过时
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUdaa1R3PT06MjViNmVhMGY=


class BulkEditOperation(str, Enum):
    """
    批量编辑操作符

    用于批量编辑测试用例时指定字段的处理方式
    """
    IGNORE = "ignore"     # 保持现有值不变
    REPLACE = "replace"   # 用提供的值覆盖当前值
    ADD = "add"           # 将提供的值追加到现有列表（多值字段）
    REMOVE = "remove"     # 从现有列表中移除指定的值（多值字段）


class ExportStatus(str, Enum):
    """
    导出任务状态

    用于标识 BDD 测试用例导出任务的状态
    """
    PENDING = "pending"       # 等待处理
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


class TestRunState(str, Enum):
    """
    测试运行状态

    用于标识测试运行的执行状态
    参考: https://www.browserstack.com/docs/test-management/api-reference/test-runs
    """
    NEW_RUN = "new_run"           # 新建运行
    IN_PROGRESS = "in_progress"   # 进行中
    UNDER_REVIEW = "under_review" # 审核中
    REJECTED = "rejected"         # 已拒绝
    DONE = "done"                 # 已完成
    CLOSED = "closed"             # 已关闭


class TestRunActiveState(str, Enum):
    """
    测试运行活跃状态

    用于标识测试运行是否处于活跃状态
    """
    ACTIVE = "active"   # 活跃状态
    CLOSED = "closed"   # 已关闭


class TestResultStatus(str, Enum):
    """
    测试结果状态

    用于标识单个测试用例在测试运行中的执行结果
    参考: https://www.browserstack.com/docs/test-management/api-reference/test-results

    官方 API 支持的状态值:
    - passed: 测试通过
    - failed: 测试失败
    - skipped: 测试跳过
    - blocked: 测试被阻塞
    - not_executed: 未执行
    """
    PASSED = "passed"             # 通过
    FAILED = "failed"             # 失败
    SKIPPED = "skipped"           # 跳过
    BLOCKED = "blocked"           # 阻塞
    NOT_EXECUTED = "not_executed" # 未执行

# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUdaa1R3PT06MjViNmVhMGY=

class TestPlanStatus(str, Enum):
    """
    测试计划状态

    用于标识测试计划的当前状态
    参考: https://www.browserstack.com/docs/test-management/api-reference/test-plans
    """
    DRAFT = "draft"           # 草稿
    ACTIVE = "active"         # 活跃
    COMPLETED = "completed"   # 已完成
    ARCHIVED = "archived"     # 已归档


class TestPlanActiveState(str, Enum):
    """
    测试计划活跃状态

    用于标识测试计划是否处于活跃状态
    """
    ACTIVE = "active"   # 活跃状态
    CLOSED = "closed"   # 已关闭


class RequirementAnalysisStatus(str, Enum):
    """
    需求分析状态
    
    用于标识需求分析报告的当前状态
    """
    DRAFT = "draft"           # 草稿
    IN_REVIEW = "in_review"   # 审核中
    APPROVED = "approved"     # 已批准
    REJECTED = "rejected"     # 已拒绝
    ARCHIVED = "archived"     # 已归档


class DefectAnalysisStatus(str, Enum):
    """
    缺陷分析状态
    
    用于标识缺陷分析报告的当前状态
    """
    DRAFT = "draft"           # 草稿
    IN_REVIEW = "in_review"   # 审核中
    APPROVED = "approved"     # 已批准
    REJECTED = "rejected"     # 已拒绝
    ARCHIVED = "archived"     # 已归档


class DefectSeverity(str, Enum):
    """
    缺陷严重程度
    
    用于标识缺陷的严重程度
    """
    BLOCKER = "blocker"       # 阻塞级别
    CRITICAL = "critical"     # 严重
    MAJOR = "major"           # 主要
    MINOR = "minor"           # 次要
    TRIVIAL = "trivial"       # 轻微


class DefectPriority(str, Enum):
    """
    缺陷优先级
    
    用于标识缺陷的处理优先级
    """
    URGENT = "urgent"   # 紧急
    HIGH = "high"       # 高
    MEDIUM = "medium"   # 中
    LOW = "low"         # 低


class DefectType(str, Enum):
    """
    缺陷类型
    
    用于分类缺陷的类型
    """
    FUNCTIONAL = "functional"     # 功能缺陷
    PERFORMANCE = "performance"   # 性能缺陷
    SECURITY = "security"         # 安全缺陷
    USABILITY = "usability"       # 可用性缺陷
    COMPATIBILITY = "compatibility" # 兼容性缺陷
    UI = "ui"                     # UI 缺陷
    DATA = "data"                 # 数据缺陷
    INTEGRATION = "integration"   # 集成缺陷
    OTHER = "other"               # 其他类型
