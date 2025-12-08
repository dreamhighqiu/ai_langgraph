"""K6 integration layer for performance testing.

This module provides K6-specific components including:
- Scenario and executor definitions
- Protocol handlers (HTTP, WebSocket, gRPC)
- Browser testing support
- Output integrations
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


from k6_agent.k6.scenarios import (
    K6Options,
    K6Scenario,
    ExecutorType,
    Stage,
    CustomMetric,
    MetricType,
    TestData,
    Threshold,
    create_smoke_test_options,
    create_load_test_options,
    create_stress_test_options,
    create_spike_test_options,
    create_soak_test_options,
    create_breakpoint_test_options,
)
# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V21neGJ3PT06MmNjNDIyZjc=

__all__ = [
    # Core types
    "K6Options",
    "K6Scenario",
    "ExecutorType",
    "Stage",
    "CustomMetric",
    "MetricType",
    "TestData",
    "Threshold",
    # Factory functions
    "create_smoke_test_options",
    "create_load_test_options",
    "create_stress_test_options",
    "create_spike_test_options",
    "create_soak_test_options",
    "create_breakpoint_test_options",
]
# fmt: off  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V21neGJ3PT06MmNjNDIyZjc=

