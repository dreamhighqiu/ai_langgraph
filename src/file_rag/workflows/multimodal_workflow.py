"""
多模态对话工作流构建模块
"""
from typing import Literal
from langgraph.graph import StateGraph, START, END
from file_rag.models import ConversationState
from file_rag.nodes import (
    route_node,
    image_processing_node,
    pdf_processing_node,
    text_processing_node,
    automated_test_node,
    browser_operation_node,
    testcase_generation_bridge_node
)


def route_by_file_type(state: ConversationState) -> Literal["image_processing", "pdf_processing", "text_processing", "automated_test", "browser_operation", "testcase_generation"]:
    """
    智能条件边：根据文件类型和任务类型决定下一个节点

    路由逻辑：
    1. testcase_generation → 测试用例生成工作流（编写测试用例）
    2. automated_test → 自动化测试节点（打开网站执行测试并生成报告）
    3. browser_operation → 浏览器操作节点（执行浏览器操作，不生成测试报告）
    4. image → 图片处理节点
    5. pdf → PDF处理节点
    6. text → 文本对话节点

    Args:
        state: 当前对话状态

    Returns:
        下一个节点的名称
    """
    file_type = state.get("file_type", "text")

    print(f"\n=== 条件边：智能路由决策 ===")
    print(f"检测到的类型: {file_type}")

    if file_type == "testcase_generation":
        print("✅ 决策: 路由到测试用例生成工作流")
        print("   → 将执行：生成用例 → 评审 → 保存到Excel")
        return "testcase_generation"
    elif file_type == "automated_test":
        print("✅ 决策: 路由到自动化测试节点")
        print("   → 将执行：使用 MCP Chrome 工具执行自动化测试并生成报告")
        return "automated_test"
    elif file_type == "browser_operation":
        print("✅ 决策: 路由到浏览器操作节点")
        print("   → 将执行：使用 MCP Chrome 工具执行浏览器操作")
        return "browser_operation"
    elif file_type == "image":
        print("✅ 决策: 路由到图片处理节点")
        print("   → 将执行：使用豆包多模态模型处理图片")
        return "image_processing"
    elif file_type == "pdf":
        print("✅ 决策: 路由到PDF处理节点")
        print("   → 将执行：提取PDF内容后使用DeepSeek模型")
        return "pdf_processing"
    else:
        print("✅ 决策: 路由到文本对话节点")
        print("   → 将执行：使用DeepSeek模型处理文本对话")
        return "text_processing"


def build_multimodal_workflow(enable_mcp: bool = True):
    """
    构建多模态对话工作流

    工作流结构:
    START → 路由节点 → 条件边 → [图片处理 | PDF处理 | 文本处理 | 自动化测试 | 浏览器操作 | 测试用例生成] → END

    支持的功能:
    1. 图片对话 - 使用豆包多模态模型处理图片
    2. PDF文档对话 - 提取文本和图片内容后使用DeepSeek模型
    3. 纯文本对话 - 使用DeepSeek模型
    4. 自动化测试 - 使用DeepSeek + MCP Chrome工具执行测试任务并生成报告
    5. 浏览器操作 - 使用DeepSeek + MCP Chrome工具执行浏览器操作（不生成测试报告）
    6. 测试用例生成 - 智能生成、评审、保存测试用例

    Args:
        enable_mcp: 是否启用 MCP 工具（默认 True）

    Returns:
        编译后的工作流应用
    """
    print("\n" + "="*80)
    print("开始构建多模态对话工作流...")
    print("="*80)

    # MCP 工具将在需要时异步加载（在 automated_test_node 中）
    if enable_mcp:
        print("\n[可选功能] MCP 工具将在需要时动态加载")
    else:
        print("\n[MCP] MCP 功能已禁用")

    # 创建状态图
    workflow = StateGraph(ConversationState)

    # 添加节点
    print("\n添加节点...")
    workflow.add_node("route", route_node)  # 节点1：路由节点
    workflow.add_node("image_processing", image_processing_node)  # 节点2：图片处理
    workflow.add_node("pdf_processing", pdf_processing_node)  # 节点3：PDF处理
    workflow.add_node("text_processing", text_processing_node)  # 节点4：文本处理
    workflow.add_node("automated_test", automated_test_node)  # 节点5：自动化测试
    workflow.add_node("browser_operation", browser_operation_node)  # 节点6：浏览器操作（新增）
    workflow.add_node("testcase_generation", testcase_generation_bridge_node)  # 节点7：测试用例生成

    # 添加边
    print("添加边...")
    # START → 路由节点
    workflow.add_edge(START, "route")

    # 路由节点 → 条件边 → 各处理节点
    workflow.add_conditional_edges(
        "route",  # 从路由节点出发
        route_by_file_type,  # 条件判断函数
        {
            "image_processing": "image_processing",  # 图片 → 图片处理节点
            "pdf_processing": "pdf_processing",  # PDF → PDF处理节点
            "text_processing": "text_processing",  # 文本 → 文本处理节点
            "automated_test": "automated_test",  # 自动化测试 → 自动化测试节点
            "browser_operation": "browser_operation",  # 浏览器操作 → 浏览器操作节点（新增）
            "testcase_generation": "testcase_generation"  # 测试用例生成 → 测试用例生成节点
        }
    )

    # 各处理节点 → END
    workflow.add_edge("image_processing", END)
    workflow.add_edge("pdf_processing", END)
    workflow.add_edge("text_processing", END)
    workflow.add_edge("automated_test", END)
    workflow.add_edge("browser_operation", END)  # 新增
    workflow.add_edge("testcase_generation", END)

    # 编译工作流
    print("编译工作流...")
    app = workflow.compile()

    print("\n" + "="*80)
    print("多模态对话工作流构建完成！")
    print("="*80)
    print("\n工作流结构:")
    print("START → 路由节点 → 智能条件边 → [图片处理 | PDF处理 | 文本处理 | 自动化测试 | 浏览器操作 | 测试用例生成] → END")
    print("\n支持的功能:")
    print("  1. 图片对话 - 使用豆包多模态模型")
    print("  2. PDF文档对话 - 提取文本和图片内容后使用DeepSeek模型")
    print("  3. 纯文本对话 - 使用DeepSeek模型")
    print("  4. 自动化测试 - 使用DeepSeek + MCP Chrome工具执行测试任务并生成报告")
    print("  5. 浏览器操作 - 使用DeepSeek + MCP Chrome工具执行浏览器操作（新增）")
    print("  6. 测试用例生成 - 智能生成、评审、保存测试用例")
    if enable_mcp:
        print(f"  7. MCP 工具 - 将在需要时动态加载")
    print("\n智能路由规则:")
    print("  • 上传图片/PDF + 编写测试用例 → 测试用例生成工作流")
    print("  • 纯文本 + 编写测试用例 → 测试用例生成工作流")
    print("  • 打开网站 + 测试关键词 → 自动化测试节点（生成测试报告）")
    print("  • 打开网站 + 无测试关键词 → 浏览器操作节点（只执行操作）")
    print("  • 上传图片（无测试用例关键词）→ 图片处理节点")
    print("  • 上传PDF（无测试用例关键词）→ PDF处理节点")
    print("  • 普通对话 → 文本处理节点")
    print("="*80 + "\n")

    return app

