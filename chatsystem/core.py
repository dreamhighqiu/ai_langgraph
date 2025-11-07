"""
多模态对话系统核心模块
基于 LangGraph 实现条件路由的完整对话系统

改进：使用 @before_model 中间件在模型调用前检测文件类型
"""

import logging
from typing import Any, Dict, List, Optional, Annotated

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from chatsystem.types import FileType, ProcessorType, ChatResult, ChatMessage
from chatsystem.detectors import FileTypeDetector
from chatsystem.middleware import detect_file_type_before_model, get_current_chat_type

logger = logging.getLogger(__name__)


class MultimodalChatSystem:
    """
    多模态对话系统

    支持三种对话模式:
    1. 图片对话 - 使用 GPT-4O 进行多模态分析
    2. PDF 对话 - 使用 GPT-4O 进行文档分析和多模态内容提取
    3. 普通对话 - 使用 DeepSeek 进行通用对话

    关键特性:
    - 在同一个聊天过程中支持多种对话模式切换
    - 只检测最后一条消息的文件类型（确定当前对话模式）
    - 保留完整的消息历史用于上下文
    - 自动路由到对应的处理器

    使用示例:
        system = MultimodalChatSystem()

        # 普通对话
        messages = [HumanMessage(content="你好")]
        result = system.chat(messages)

        # 图片对话
        messages = [HumanMessage(content=[
            {"type": "text", "text": "这是什么?"},
            {"type": "file", "mime_type": "image/png", "data": "...base64..."}
        ])]
        result = system.chat(messages)

        # 继续文本对话（在同一个聊天过程中）
        messages.append(HumanMessage(content="告诉我更多信息"))
        result = system.chat(messages)  # 会自动切换到文本模式
    """

    def __init__(self):
        """初始化多模态对话系统"""
        logger.info("初始化多模态对话系统")

        # 创建图表
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()

        logger.info("多模态对话系统初始化完成")
    
    def _build_graph(self) -> StateGraph:
        """
        构建 LangGraph 图
        
        节点流程:
        START -> 文件类型检测 -> 条件路由 -> 具体处理节点 -> END
        """
        graph = StateGraph(dict)
        
        # 添加节点
        graph.add_node("detect_file_type", self._detect_file_type)
        graph.add_node("process_image", self._process_image)
        graph.add_node("process_pdf", self._process_pdf)
        graph.add_node("process_text", self._process_text)
        
        # 添加边
        graph.add_edge(START, "detect_file_type")
        
        # 条件路由
        graph.add_conditional_edges(
            "detect_file_type",
            self._route_by_file_type,
            {
                "image": "process_image",
                "pdf": "process_pdf",
                "text": "process_text",
            }
        )
        
        # 所有处理节点都连接到 END
        graph.add_edge("process_image", END)
        graph.add_edge("process_pdf", END)
        graph.add_edge("process_text", END)
        
        return graph
    
    def _detect_file_type(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测文件类型节点

        关键逻辑:
        - 调用中间件函数检测当前聊天类型
        - 始终获取最后一条消息
        - 检测最后一条消息的文件类型
        - 这样可以在同一个聊天过程中支持模式切换
        - 例如: 先上传图片 -> 分析图片 -> 继续文本对话

        改进:
        - 使用 detect_file_type_before_model() 中间件函数
        - 确保每次都检测最后一条消息，避免状态混乱
        """
        logger.info("执行节点: 文件类型检测")

        # 使用中间件函数检测当前聊天类型
        state = detect_file_type_before_model(state)

        return state
    
    def _route_by_file_type(self, state: Dict[str, Any]) -> str:
        """根据文件类型路由"""
        file_type = state.get("file_type", FileType.UNKNOWN)
        
        if file_type == FileType.IMAGE:
            return "image"
        elif file_type == FileType.PDF:
            return "pdf"
        else:
            return "text"
    
    def _process_image(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """处理图片对话节点"""
        logger.info("执行节点: 处理图片")

        from chatsystem.processors import ProcessorFactory

        messages = state.get("messages", [])
        processor = ProcessorFactory.create_processor(FileType.IMAGE)
        response = processor.process(messages)

        state["response"] = response
        state["processor_type"] = ProcessorType.IMAGE
        state["current_node"] = "process_image"

        return state

    def _process_pdf(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """处理 PDF 对话节点"""
        logger.info("执行节点: 处理 PDF")

        from chatsystem.processors import ProcessorFactory

        messages = state.get("messages", [])
        processor = ProcessorFactory.create_processor(FileType.PDF)
        response = processor.process(messages)

        state["response"] = response
        state["processor_type"] = ProcessorType.PDF
        state["current_node"] = "process_pdf"

        return state

    def _process_text(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """处理普通文本对话节点"""
        logger.info("执行节点: 处理文本")

        from chatsystem.processors import ProcessorFactory

        messages = state.get("messages", [])
        processor = ProcessorFactory.create_processor(FileType.TEXT)
        response = processor.process(messages)

        state["response"] = response
        state["processor_type"] = ProcessorType.TEXT
        state["current_node"] = "process_text"

        return state
    
    def chat(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """
        执行对话
        
        参数:
            messages: 消息列表
        
        返回:
            {
                "messages": 消息列表,
                "file_type": 检测到的文件类型,
                "processor_type": 使用的处理器类型,
                "current_node": 使用的处理节点,
                "response": 对话响应
            }
        """
        logger.info(f"开始对话，消息数: {len(messages)}")
        
        # 初始化状态
        state = {
            "messages": messages,
            "file_type": FileType.UNKNOWN,
            "processor_type": None,
            "current_node": None,
            "response": None,
        }
        
        # 执行图表
        result = self.compiled_graph.invoke(state)
        
        logger.info(f"对话完成，使用节点: {result.get('current_node')}")
        
        return result
    
    def get_response(self, messages: List[BaseMessage]) -> str:
        """获取对话响应文本"""
        result = self.chat(messages)
        return result.get("response", "")


# 全局实例
_system_instance = None


def get_chat_system() -> MultimodalChatSystem:
    """获取全局对话系统实例"""
    global _system_instance
    if _system_instance is None:
        _system_instance = MultimodalChatSystem()
    return _system_instance


def chat(messages: List[BaseMessage]) -> Dict[str, Any]:
    """执行对话的便捷函数"""
    system = get_chat_system()
    return system.chat(messages)


def get_response(messages: List[BaseMessage]) -> str:
    """获取对话响应的便捷函数"""
    system = get_chat_system()
    return system.get_response(messages)


# ============================================================================
# LangGraph API 兼容导出
# ============================================================================

def _build_langgraph_agent():
    """
    构建 LangGraph API 兼容的 agent

    这个函数被 LangGraph API 调用来创建图实例
    支持前端通过 LangGraph API 调用
    """
    # 定义状态类型，使用 Annotated 处理消息列表
    from typing import TypedDict

    class AgentState(TypedDict):
        """Agent 状态"""
        messages: Annotated[list, add_messages]
        _file_type: FileType

    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("detect_file_type", _node_detect_file_type)
    graph.add_node("process_image", _node_process_image)
    graph.add_node("process_pdf", _node_process_pdf)
    graph.add_node("process_text", _node_process_text)

    # 添加边
    graph.add_edge(START, "detect_file_type")

    # 条件路由
    graph.add_conditional_edges(
        "detect_file_type",
        _route_by_file_type,
        {
            "image": "process_image",
            "pdf": "process_pdf",
            "text": "process_text",
        }
    )

    # 所有处理节点都连接到 END
    graph.add_edge("process_image", END)
    graph.add_edge("process_pdf", END)
    graph.add_edge("process_text", END)

    return graph.compile()


def _node_detect_file_type(state: Dict[str, Any]) -> Dict[str, Any]:
    """检测文件类型节点"""
    logger.info("执行节点: 文件类型检测")

    messages = state.get("messages", [])
    file_type = FileTypeDetector.detect_from_messages(messages)

    logger.info(f"检测到文件类型: {file_type.value}")

    # 存储文件类型到状态
    state['_file_type'] = file_type

    return state


def _route_by_file_type(state: Dict[str, Any]) -> str:
    """根据文件类型路由"""
    file_type = state.get('_file_type', FileType.TEXT)

    if file_type == FileType.IMAGE:
        return "image"
    elif file_type == FileType.PDF:
        return "pdf"
    else:
        return "text"


def _node_process_image(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理图片节点"""
    logger.info("执行节点: 图片处理")

    from chatsystem.processors import ProcessorFactory

    messages = state.get("messages", [])
    processor = ProcessorFactory.create_processor(FileType.IMAGE)
    response = processor.process(messages)

    # 添加 AI 响应到消息列表
    state["messages"].append(AIMessage(content=response))

    return state


def _node_process_pdf(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理 PDF 节点"""
    logger.info("执行节点: PDF 处理")

    from chatsystem.processors import ProcessorFactory

    messages = state.get("messages", [])
    processor = ProcessorFactory.create_processor(FileType.PDF)
    response = processor.process(messages)

    # 添加 AI 响应到消息列表
    state["messages"].append(AIMessage(content=response))

    return state


def _node_process_text(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理文本节点"""
    logger.info("执行节点: 文本处理")

    from chatsystem.processors import ProcessorFactory

    messages = state.get("messages", [])
    processor = ProcessorFactory.create_processor(FileType.TEXT)
    response = processor.process(messages)

    # 添加 AI 响应到消息列表
    state["messages"].append(AIMessage(content=response))

    return state


# 创建全局 LangGraph agent 实例
_langgraph_agent = None


def get_langgraph_agent():
    """获取 LangGraph API 兼容的 agent"""
    global _langgraph_agent
    if _langgraph_agent is None:
        logger.info("构建 LangGraph agent...")
        _langgraph_agent = _build_langgraph_agent()
        logger.info("LangGraph agent 构建完成")
    return _langgraph_agent


# LangGraph API 导出
# 直接导出编译后的 agent，供 LangGraph API 使用
agent_multimodal = get_langgraph_agent()

