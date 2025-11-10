"""
多模态对话系统 - 主入口文件（重构版）

这是一个企业级智能测试平台，支持：
1. 图片对话 - 使用豆包多模态模型
2. PDF文档对话 - 提取文本和图片内容
3. 纯文本对话 - 使用DeepSeek模型
4. 自动化测试 - 使用MCP Chrome工具执行测试并生成报告
5. 浏览器操作 - 执行浏览器操作
6. 测试用例生成 - 智能生成、评审、保存测试用例

重构说明：
- 原始代码（2570行）已模块化为多个文件
- models/: 数据模型
- utils/: 工具函数
- nodes/: 工作流节点
- workflows/: 工作流构建
"""

# 导入工作流构建函数
from file_rag.workflows import build_multimodal_workflow

# ============================================
# 创建全局agent实例（供graph.json调用）
# ============================================
# 构建并导出agent，供LangGraph Server使用
agent = build_multimodal_workflow()


# ============================================
# 主程序入口
# ============================================
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    # 构建工作流
    app = build_multimodal_workflow()

    # 测试示例
    print("\n" + "="*80)
    print("测试示例")
    print("="*80)

    # 示例1: 纯文本对话
    print("\n【示例1：纯文本对话】")
    test_messages_text = [
        HumanMessage(content="你好，请介绍一下自己")
    ]

    result = app.invoke({
        "messages": test_messages_text,
        "file_type": "",
        "extracted_content": ""
    })

    print(f"\n最终回复: {result['messages'][-1].content}")

    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)

