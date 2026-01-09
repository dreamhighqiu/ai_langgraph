"""
AI生成服务 - 处理测试用例、需求分析、缺陷报告的AI生成

使用 LangGraph 智能体架构，参考 ai-test-management 项目设计
关键特性：
1. 基于 LangGraph 的智能体架构
2. 支持工具调用（创建测试用例、RAG检索等）
3. 上下文管理（自动传递 project_id、module 等）
4. 流式输出
"""
import json
import uuid
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from config.env import LangGraphConfig, OllamaConfig
from utils.log_util import logger

from module_testing.agents.testcase_agent import get_testcase_agent
from module_testing.agents.requirement_agent import get_requirement_agent
from module_testing.agents.defect_agent import get_defect_agent


class AIGenerationService:
    """AI生成服务 - 基于 LangGraph 智能体"""

    def __init__(self):
        """初始化AI服务"""
        # 获取智能体单例
        self.testcase_agent = get_testcase_agent()
        self.requirement_agent = get_requirement_agent()
        self.defect_agent = get_defect_agent()
        
        logger.info("AI生成服务初始化完成")

    async def generate(
        self,
        generation_type: str,
        input_data: Dict[str, Any],
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        兼容旧接口：同步/非流式生成入口。

        目前项目主要通过 LangGraph 流式接口对外提供能力；为避免控制器在未改造完成前
        直接报 AttributeError，这里返回结构化错误提示。
        """
        return {
            "success": False,
            "error": f"AI 生成接口暂未实现，请使用 /testing/ai-chat 相关流式接口（generation_type={generation_type}）",
            "data": None,
            "messages": [],
            "thread_id": thread_id,
        }

    def clear_session_history(self, thread_id: str) -> None:
        """
        兼容旧接口：清理会话历史。

        当前智能体会话由各 agent 的 checkpointer 管理；若需要精确清理，可在后续实现。
        """
        logger.info(f"clear_session_history called (thread_id={thread_id})")

    # ==================== 测试用例生成 ====================

    async def generate_test_case_stream(
        self,
        project_id: int,
        feature_description: str,
        module: Optional[str] = None,
        template_type: str = "normal",
        thread_id: Optional[str] = None,
        rag_context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式生成测试用例（使用 LangGraph 智能体）

        Args:
            project_id: 项目ID
            feature_description: 功能描述
            module: 模块名称
            template_type: 模板类型（normal 或 bdd）
            thread_id: 会话ID(用于连续对话)
            rag_context: RAG上下文
        """
        try:
            # 构建用户输入
            user_input = feature_description
            if rag_context:
                user_input = f"{feature_description}\n\n相关上下文:\n{rag_context}"
            
            # 生成 thread_id
            if not thread_id:
                thread_id = f"testcase_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"开始生成测试用例，project_id={project_id}, module={module}, thread_id={thread_id}")
            
            # 调用智能体生成测试用例
            async for message in self.testcase_agent.generate_test_cases(
                user_input=user_input,
                project_id=project_id,
                module=module,
                template_type=template_type,
                thread_id=thread_id
            ):
                # 处理不同类型的消息
                if isinstance(message, AIMessage):
                    # AI 回复消息
                    if message.content:
                        yield message.content
                    
                    # 如果有工具调用，显示工具调用信息
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.get("name", "unknown")
                            logger.info(f"工具调用: {tool_name}")
                            yield f"\n\n🔧 调用工具: {tool_name}\n"
                
                elif isinstance(message, ToolMessage):
                    # 工具执行结果消息
                    logger.info("工具执行完成")
                    yield f"\n✅ 工具执行完成\n"

        except Exception as e:
            logger.error(f"生成测试用例失败: {str(e)}", exc_info=True)
            yield f"\n\n❌ 生成失败: {str(e)}"

    # ==================== 需求分析生成 ====================

    async def generate_requirement_stream(
        self,
        project_id: int,
        requirement_description: str,
        module: Optional[str] = None,
        thread_id: Optional[str] = None,
        rag_context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式生成需求分析（使用 LangGraph 智能体）

        Args:
            project_id: 项目ID
            requirement_description: 需求描述
            module: 所属模块
            thread_id: 会话ID
            rag_context: RAG上下文
        """
        try:
            # 构建用户输入
            user_input = requirement_description
            if rag_context:
                user_input = f"{requirement_description}\n\n相关上下文:\n{rag_context}"
            
            # 生成 thread_id
            if not thread_id:
                thread_id = f"requirement_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"开始生成需求分析，project_id={project_id}, module={module}, thread_id={thread_id}")
            
            # 调用智能体分析需求
            async for message in self.requirement_agent.analyze_requirement(
                user_input=user_input,
                project_id=project_id,
                module=module,
                thread_id=thread_id
            ):
                # 处理不同类型的消息
                if isinstance(message, AIMessage):
                    if message.content:
                        yield message.content
                    
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.get("name", "unknown")
                            logger.info(f"工具调用: {tool_name}")
                            yield f"\n\n🔧 调用工具: {tool_name}\n"
                
                elif isinstance(message, ToolMessage):
                    logger.info("工具执行完成")
                    yield f"\n✅ 工具执行完成\n"

        except Exception as e:
            logger.error(f"生成需求分析失败: {str(e)}", exc_info=True)
            yield f"\n\n❌ 生成失败: {str(e)}"
