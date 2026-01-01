"""K6性能测试智能体平台.

基于deepagents框架和K6性能测试工具的智能体平台。

功能：
- 理解用户性能测试需求
- 通过RAG检索API接口信息
- 智能生成K6测试脚本
- 执行K6性能测试
- 深度分析测试结果
- 生成图文并茂的测试报告

使用方法：

```python
import os
from k6_agent import create_k6_agent

# 设置API密钥
os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"

# 创建智能体
agent = create_k6_agent()

# 使用智能体
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "请对登录接口进行性能测试"}
    ]
})
```

环境变量配置：

- DEEPSEEK_API_KEY: DeepSeek API密钥
- K6_RAG_MCP_URL: RAG MCP服务地址 (默认: http://127.0.0.1:8002/sse)
- K6_CHART_MCP_COMMAND: Chart MCP命令 (默认: npx)
- K6_BINARY: K6可执行文件路径 (默认: k6)
- K6_SCRIPTS_DIR: 脚本保存目录 (默认: ./k6_scripts)
- K6_RESULTS_DIR: 结果保存目录 (默认: ./k6_results)
- K6_DEFAULT_VUS: 默认虚拟用户数 (默认: 10)
- K6_DEFAULT_DURATION: 默认测试时长 (默认: 1m)
- K6_DEFAULT_P95_THRESHOLD: 默认P95阈值ms (默认: 500)
"""


# fmt: off  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2tKYVRRPT06NWYxYmVmOTQ=

from k6_agent.agent import create_k6_agent
from k6_agent.config import K6Config, DEFAULT_CONFIG
from k6_agent.tasks import K6TaskManager, get_task_manager
# type: ignore  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2tKYVRRPT06NWYxYmVmOTQ=

__version__ = "1.0.0"
__all__ = [
    "create_k6_agent",
    "K6Config",
    "DEFAULT_CONFIG",
    "K6TaskManager",
    "get_task_manager",
]
# fmt: off  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2tKYVRRPT06NWYxYmVmOTQ=

