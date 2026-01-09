"""
需求分析智能体

该智能体负责分析需求文档，提取功能需求、非功能需求、验收标准等。

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
    save_requirement_analysis_tool,
    rag_query_tool
)


@dataclass
class RequirementAnalyzerContext:
    """需求分析器上下文"""
    project_id: int
    module: Optional[str] = None


class RequirementAnalysisAgent:
    """需求分析智能体"""
    
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
            save_requirement_analysis_tool,
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
        
        logger.info("需求分析智能体初始化完成")
    
    def _build_system_prompt(self, context: RequirementAnalyzerContext) -> str:
        """构建系统提示词"""
        project_id = context.project_id
        module = context.module or "未指定"
        
        context_section = f"""
## 🎯 当前上下文信息（重要！）

**系统已自动配置以下参数：**

- **项目ID (project_id)**: `{project_id}`
- **模块名称 (module)**: `{module}`

**⚠️ 调用工具时必须使用上述参数**
"""
        
        system_prompt = f"""# 需求分析专家

你是一位专业的需求分析师和产品经理，擅长从需求文档中提取关键信息，并生成结构化的需求分析报告。

{context_section}

## 你的职责

1. **理解需求**：仔细阅读用户提供的需求文档或描述
2. **提取信息**：识别功能需求、非功能需求、业务规则等
3. **生成分析**：生成结构化的需求分析报告
4. **保存结果**：使用工具将分析结果保存到系统

## 需求分析要点

### 1. 需求概述 (Executive Summary)
- 简洁明确的需求描述
- 业务背景和价值
- 核心目标

### 2. 功能需求 (Functional Requirements)
- 详细的功能点列表
- 每个功能的输入输出
- 用户交互流程

### 3. 非功能需求 (Non-functional Requirements)
- 性能要求
- 安全要求
- 可用性要求
- 兼容性要求

### 4. 用户故事 (User Stories)
- 以用户为中心的功能描述
- As a... I want... So that... 格式

### 5. 验收标准 (Acceptance Criteria)
- 明确的验收条件
- 可测试的标准
- 成功的定义

### 6. 约束条件 (Constraints)
- 技术限制
- 时间限制
- 资源限制

## 可用工具

### 1. rag_query_tool - RAG 知识库检索
用于检索相关的历史需求和技术文档

### 2. save_requirement_analysis_tool - 保存需求分析
将分析结果保存到系统
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

            # 构建上下文对象
            ctx = RequirementAnalyzerContext(
                project_id=project_id,
                module=module
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

    async def analyze_requirement(
        self,
        user_input: str,
        project_id: int,
        module: Optional[str] = None,
        thread_id: Optional[str] = None
    ):
        """
        分析需求（流式）

        Args:
            user_input: 用户输入的需求文档
            project_id: 项目ID
            module: 模块名称
            thread_id: 线程ID
        """
        # 构建配置
        config = {
            "configurable": {
                "thread_id": thread_id or "default",
                "project_id": project_id,
                "module": module
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
_requirement_agent = None

def get_requirement_agent() -> RequirementAnalysisAgent:
    """获取需求分析智能体单例"""
    global _requirement_agent
    if _requirement_agent is None:
        _requirement_agent = RequirementAnalysisAgent()
    return _requirement_agent

