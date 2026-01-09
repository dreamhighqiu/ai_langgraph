"""
缺陷分析智能体

该智能体负责分析缺陷报告，进行根本原因分析、影响分析、修复建议等。

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

from config.env import LLMConfig
from utils.log_util import logger
from module_testing.agents.tools import (
    save_defect_analysis_tool,
    rag_query_tool
)


@dataclass
class DefectAnalyzerContext:
    """缺陷分析器上下文"""
    project_id: int
    module: Optional[str] = None


class DefectAnalysisAgent:
    """缺陷分析智能体"""
    
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
            save_defect_analysis_tool,
            rag_query_tool
        ]
        
        # 绑定工具到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 构建 LangGraph
        self.graph = self._build_graph()
        
        # 编译 graph（不使用自定义 checkpointer，LangGraph API 会自动处理）
        self.app = self.graph.compile()
        
        logger.info("缺陷分析智能体初始化完成")
    
    def _build_system_prompt(self, context: DefectAnalyzerContext) -> str:
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
        
        system_prompt = f"""# 缺陷分析专家

你是一位专业的缺陷分析师和质量保证专家，擅长从缺陷报告中识别根本原因，提供修复建议和预防措施。

{context_section}

## 你的职责

1. **理解缺陷**：仔细分析用户提供的缺陷报告或描述
2. **根本原因分析**：识别缺陷的根本原因
3. **影响分析**：评估缺陷的影响范围和严重程度
4. **提供建议**：生成修复建议、测试建议和预防措施
5. **保存分析**：使用工具将分析结果保存到系统

## 缺陷分析要点

### 1. 缺陷概述 (Executive Summary)
- 简洁明确的缺陷描述
- 缺陷类型和分类
- 严重程度和优先级

### 2. 根本原因分析 (Root Cause Analysis)
- 5 Why 分析法
- 鱼骨图分析
- 代码层面的原因
- 流程层面的原因

### 3. 影响分析 (Impact Analysis)
- 受影响的功能模块
- 用户影响范围
- 业务影响评估
- 技术债务分析

### 4. 复现步骤 (Reproduction Steps)
- 详细的复现步骤
- 环境要求
- 测试数据

### 5. 修复建议 (Fix Recommendations)
- 短期修复方案
- 长期优化方案
- 代码改进建议

### 6. 测试建议 (Testing Suggestions)
- 回归测试建议
- 边界测试建议
- 性能测试建议

### 7. 预防措施 (Prevention Measures)
- 代码审查改进
- 测试流程改进
- 开发流程改进

## 可用工具

### 1. rag_query_tool - RAG 知识库检索
用于检索相似的历史缺陷和解决方案

### 2. save_defect_analysis_tool - 保存缺陷分析
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
            ctx = DefectAnalyzerContext(
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

    async def analyze_defect(
        self,
        user_input: str,
        project_id: int,
        module: Optional[str] = None,
        thread_id: Optional[str] = None
    ):
        """
        分析缺陷（流式）

        Args:
            user_input: 用户输入的缺陷报告
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
_defect_agent = None

def get_defect_agent() -> DefectAnalysisAgent:
    """获取缺陷分析智能体单例"""
    global _defect_agent
    if _defect_agent is None:
        _defect_agent = DefectAnalysisAgent()
    return _defect_agent


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
        save_defect_analysis_tool,
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
        save_defect_analysis_tool,
        rag_query_tool
    ]
    
    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 构建 workflow
    workflow = StateGraph(MessagesState)
    
    def call_model(state: MessagesState, config):
        """调用模型"""
        # 从配置中获取上下文
        ctx = config.get("configurable", {})
        project_id = ctx.get("project_id", 0)
        module = ctx.get("module", "未指定")
        
        system_prompt = f"""# 缺陷分析专家

你是一位专业的缺陷分析师，擅长分析缺陷报告，进行根本原因分析、影响分析、修复建议等。

## 当前上下文
- 项目ID: {project_id}
- 模块: {module}

## 分析原则
1. 识别缺陷根本原因
2. 评估影响范围
3. 提供修复建议
4. 建议预防措施
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
# langgraph.json 中配置: "path": "./module_testing/agents/defect_agent.py:agent"
agent = _create_langgraph_app_for_api()

