"""
测试用例生成智能体

该智能体负责根据需求文档、用户故事或功能描述自动生成测试用例。
支持普通测试用例和 BDD 测试用例两种格式。

架构参考: ai-test-management 项目
"""

import os
from dataclasses import dataclass
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from config.env import LLMConfig
from utils.log_util import logger
from module_testing.agents.tools import (
    create_test_case_tool,
    update_test_case_tool,
    batch_create_test_cases_tool,
    rag_query_tool
)


@dataclass
class TestCaseGeneratorContext:
    """测试用例生成器上下文"""
    project_id: int
    module: Optional[str] = None
    template_type: str = "normal"  # normal 或 bdd


class TestCaseAgent:
    """测试用例生成智能体"""
    
    def __init__(self):
        """初始化智能体"""
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=LLMConfig.llm_model_name,
            api_key=LLMConfig.llm_api_key,
            base_url=LLMConfig.llm_base_url,
            temperature=LLMConfig.llm_temperature,
            streaming=True
        )
        
        # 定义工具列表
        self.tools = [
            create_test_case_tool,
            update_test_case_tool,
            batch_create_test_cases_tool,
            rag_query_tool
        ]
        
        # 绑定工具到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 构建 LangGraph
        self.graph = self._build_graph()
        
        # 内存检查点
        self.memory = MemorySaver()
        
        # 编译 graph
        self.app = self.graph.compile(checkpointer=self.memory)
        
        logger.info("测试用例生成智能体初始化完成")
    
    def _build_system_prompt(self, context: TestCaseGeneratorContext) -> str:
        """构建系统提示词"""
        project_id = context.project_id
        module = context.module or "未指定"
        template_type = context.template_type
        
        context_section = f"""
## 🎯 当前上下文信息（重要！）

**系统已自动配置以下参数，调用工具时必须使用这些值：**

- **项目ID (project_id)**: `{project_id}`
- **模块名称 (module)**: `{module}`
- **默认模板类型 (template_type)**: `{template_type}`

**⚠️ 调用工具时的关键注意事项：**

1. **必须使用上述参数**：创建测试用例时，`project_id` 必须使用上面显示的值
2. **不要询问用户**：这些参数已由系统自动传入，不需要用户手动提供
3. **模板类型**：
   - 如果 template_type 是 `normal`，创建普通测试用例
   - 如果 template_type 是 `bdd`，创建 BDD 测试用例
   - 用户可以在对话中要求使用特定模板，但默认使用上述值
"""
        
        system_prompt = f"""# 测试用例生成专家

你是一位专业的软件测试工程师和测试用例设计专家，擅长根据需求文档、用户故事或功能描述生成高质量的测试用例。

{context_section}

## 你的职责

1. **理解需求**：仔细分析用户提供的需求文档、用户故事或功能描述
2. **设计测试用例**：根据需求设计全面、合理的测试用例
3. **创建测试用例**：使用提供的工具将测试用例保存到系统中（使用上述上下文参数）
4. **更新测试用例**：根据反馈优化和更新已有的测试用例

## 测试用例设计原则

### 1. 全面性
- 覆盖正常流程（Happy Path）
- 覆盖异常流程（Error Path）
- 覆盖边界条件（Boundary Conditions）
- 覆盖特殊场景（Special Cases）

### 2. 清晰性
- 测试用例名称简洁明了，能够清楚表达测试目的
- 测试步骤描述清晰，易于执行
- 预期结果明确，可验证

### 3. 独立性
- 每个测试用例应该独立可执行
- 不依赖其他测试用例的执行结果
- 包含必要的前置条件

## 可用工具

你有以下工具可以使用：

### 1. rag_query_tool - RAG 知识库检索
用于从知识库检索相关的上下文信息，帮助生成更准确的测试用例。

**使用场景**：
- 当用户提到具体的 API 接口名称时
- 需要了解接口的技术细节、参数格式等
- 查找历史测试数据和性能基准

### 2. create_test_case_tool - 创建测试用例
用于创建新的测试用例。

### 3. update_test_case_tool - 更新测试用例
用于更新已有的测试用例。

### 4. batch_create_test_cases_tool - 批量创建测试用例
用于一次性创建多个测试用例，提高效率。

## 工作流程

### 标准流程
1. **接收需求**：用户提供需求文档、用户故事或功能描述
2. **RAG 检索**（可选）：如果用户提到具体的 API 接口或功能模块，使用 rag_query_tool 检索相关信息
3. **分析需求**：理解功能点、业务规则、边界条件
4. **设计测试用例**：识别测试场景，确定测试类型和优先级
5. **创建测试用例**：使用工具创建测试用例（必须使用上下文中的 project_id）
6. **确认结果**：向用户报告创建的测试用例信息

现在，请等待用户的需求，然后开始你的工作！
"""
        return system_prompt

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph"""
        workflow = StateGraph(MessagesState)

        # 定义智能体节点
        def call_model(state: MessagesState, config: RunnableConfig):
            """调用模型"""
            # 从配置中获取上下文
            context = config.get("configurable", {})
            project_id = context.get("project_id", 0)
            module = context.get("module")
            template_type = context.get("template_type", "normal")

            # 构建上下文对象
            ctx = TestCaseGeneratorContext(
                project_id=project_id,
                module=module,
                template_type=template_type
            )

            # 构建系统提示词
            system_prompt = self._build_system_prompt(ctx)

            # 构建消息
            messages = [{"role": "system", "content": system_prompt}] + state["messages"]

            # 调用 LLM
            response = self.llm_with_tools.invoke(messages)

            return {"messages": [response]}

        # 定义路由函数
        def should_continue(state: MessagesState):
            """判断是否继续执行"""
            messages = state["messages"]
            last_message = messages[-1]

            # 如果有工具调用，继续执行工具
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"

            # 否则结束
            return END

        # 添加节点
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # 添加边
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")

        return workflow

    async def generate_test_cases(
        self,
        user_input: str,
        project_id: int,
        module: Optional[str] = None,
        template_type: str = "normal",
        thread_id: Optional[str] = None
    ):
        """
        生成测试用例（流式）

        Args:
            user_input: 用户输入
            project_id: 项目ID
            module: 模块名称
            template_type: 模板类型
            thread_id: 线程ID（用于会话管理）
        """
        # 构建配置
        config = {
            "configurable": {
                "thread_id": thread_id or "default",
                "project_id": project_id,
                "module": module,
                "template_type": template_type
            }
        }

        # 构建输入
        input_data = {
            "messages": [{"role": "user", "content": user_input}]
        }

        # 流式执行
        async for event in self.app.astream(input_data, config, stream_mode="values"):
            # 获取最后一条消息
            messages = event.get("messages", [])
            if messages:
                last_message = messages[-1]
                yield last_message


# 全局单例
_testcase_agent = None

def get_testcase_agent() -> TestCaseAgent:
    """获取测试用例生成智能体单例"""
    global _testcase_agent
    if _testcase_agent is None:
        _testcase_agent = TestCaseAgent()
    return _testcase_agent


# ============================================
# LangGraph CLI 导出 (用于 langgraph.json)
# ============================================

def _create_langgraph_app_for_api():
    """
    创建 LangGraph 应用实例（供 LangGraph API 使用）
    
    注意：LangGraph API 会自动处理持久化，不需要自定义 checkpointer
    """
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langgraph.prebuilt import ToolNode
    from config.env import LLMConfig
    from module_testing.agents.tools import (
        create_test_case_tool,
        update_test_case_tool,
        batch_create_test_cases_tool,
        rag_query_tool
    )
    
    # 初始化 LLM
    llm = ChatOpenAI(
        model=LLMConfig.llm_model_name,
        api_key=LLMConfig.llm_api_key,
        base_url=LLMConfig.llm_base_url,
        temperature=LLMConfig.llm_temperature,
        streaming=True
    )
    
    # 定义工具列表
    tools = [
        create_test_case_tool,
        update_test_case_tool,
        batch_create_test_cases_tool,
        rag_query_tool
    ]
    
    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 构建 workflow
    workflow = StateGraph(MessagesState)
    
    def call_model(state: MessagesState, config):
        """调用模型"""
        from langchain_core.runnables import RunnableConfig
        
        # 从配置中获取上下文
        ctx = config.get("configurable", {})
        project_id = ctx.get("project_id", 0)
        module = ctx.get("module", "未指定")
        template_type = ctx.get("template_type", "normal")
        
        system_prompt = f"""# 测试用例生成专家

你是一位专业的软件测试工程师，擅长根据需求生成高质量的测试用例。

## 当前上下文
- 项目ID: {project_id}
- 模块: {module}
- 模板类型: {template_type}

## 工具使用说明
调用工具时必须使用上述 project_id 参数。

## 测试用例设计原则
1. 覆盖正常流程和异常流程
2. 覆盖边界条件
3. 测试用例名称清晰
4. 预期结果明确可验证
"""
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: MessagesState):
        """判断是否继续执行"""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    # 添加节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # 添加边
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    
    # 编译时不使用 checkpointer（LangGraph API 会自动处理）
    return workflow.compile()

# 导出给 LangGraph CLI 使用
# langgraph.json 中配置: "path": "./module_testing/agents/testcase_agent.py:agent"
agent = _create_langgraph_app_for_api()

