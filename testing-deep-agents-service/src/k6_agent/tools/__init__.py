"""Agent tools for K6 performance testing.

This module provides LangChain-compatible tools for:
- K6 script generation
- Test execution
- Result analysis
- Report and chart generation
- Knowledge retrieval
- API query from knowledge base (anything-chat-rag)
- Test data generation (Faker style)
"""


# pylint: disable  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U3pCQ1dBPT06NDBiNDQzMjY=

from k6_agent.tools.k6_tools import (
    K6ScriptGenerator,
    ApiEndpoint,
    HttpMethod,
    create_k6_script_tool,
    create_k6_validation_tool,
)
from k6_agent.tools.execution_tools import (
    create_k6_run_tool,
    create_k6_cloud_tool,
)
from k6_agent.tools.analysis_tools import (
    create_result_parser_tool,
    create_metrics_analyzer_tool,
)
from k6_agent.tools.report_tools import (
    create_chart_generation_tool,
    create_report_generation_tool,
    create_quick_summary_tool,
)
from k6_agent.tools.api_query_tools import (
    api_query_tools,
    query_api_from_knowledge_base,
    generate_test_data,
    parse_api_for_k6_script,
)
# pragma: no cover  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U3pCQ1dBPT06NDBiNDQzMjY=

__all__ = [
    # K6 script tools
    "K6ScriptGenerator",
    "ApiEndpoint",
    "HttpMethod",
    "create_k6_script_tool",
    "create_k6_validation_tool",
    # Execution tools
    "create_k6_run_tool",
    "create_k6_cloud_tool",
    # Analysis tools
    "create_result_parser_tool",
    "create_metrics_analyzer_tool",
    # Report and chart tools
    "create_chart_generation_tool",
    "create_report_generation_tool",
    "create_quick_summary_tool",
    # API query and data generation tools
    "api_query_tools",
    "query_api_from_knowledge_base",
    "generate_test_data",
    "parse_api_for_k6_script",
]

# type: ignore  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U3pCQ1dBPT06NDBiNDQzMjY=
