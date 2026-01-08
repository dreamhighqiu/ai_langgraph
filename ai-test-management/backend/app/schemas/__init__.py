"""
Pydantic 模式定义模块

包含所有 API 请求和响应的数据模型
"""


# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UjFKWVN3PT06OTc1Zjc2ZDA=

from .common import (
    BaseResponse,
    ErrorResponse,
    SuccessResponse,
    MessageResponse,
)
from .pagination import (
    PaginationInfo,
    PaginatedResponse,
    PaginationParams,
)
from .enums import (
    Priority,
    TestCaseState,
    TestCaseType,
    TestRunState,
    TestRunActiveState,
    TestResultStatus,
)

__all__ = [
    # 通用响应
    "BaseResponse",
    "ErrorResponse",
    "SuccessResponse",
    "MessageResponse",
    # 分页
    "PaginationInfo",
    "PaginatedResponse",
    "PaginationParams",
    # 枚举
    "Priority",
    "TestCaseState",
    "TestCaseType",
    "TestRunState",
    "TestRunActiveState",
    "TestResultStatus",
]

# fmt: off  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UjFKWVN3PT06OTc1Zjc2ZDA=
