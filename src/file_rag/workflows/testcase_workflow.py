"""
测试用例生成工作流 - 独立的LangGraph工作流

工作流结构：
    START → 节点1(编写) → 节点2(评审) → 条件边(决策) → 节点3(保存) → END
                                              ↓
                                            节点1(重新生成)

支持功能：
1. 支持图片、PDF、纯文本三种输入
2. AI自动评审测试用例
3. 评审不通过时自动重新生成
4. 最多评审3次后强制保存
5. 保存到Excel文件

文件类型处理说明：
- file_type="image": 从消息中提取图片，使用GPT-4O多模态模型分析，生成基于图片内容的测试用例
- file_type="pdf": 从消息中提取PDF，提取文本和图片，使用GPT-4O分析，生成基于PDF内容的测试用例
- file_type="text": 使用纯文本模式，使用DeepSeek模型，基于test_requirement生成测试用例

关键字段说明：
- messages: 消息列表，包含用户上传的文件（图片/PDF）或纯文本
- file_type: 文件类型标识，由上游工作流（multimodal_workflow）检测并传入
- extracted_content: 从文件中提取的内容（可选）
- test_requirement: 测试需求描述，由上游工作流从消息中提取
"""
from langgraph.graph import StateGraph, START, END
from file_rag.models import TestCaseState
from file_rag.nodes.testcase_nodes import (
    write_test_case_node,
    review_test_case_node,
    review_decision_edge_new,
    save_to_excel_node
)


def build_testcase_workflow():
    """
    构建测试用例生成工作流

    这是一个独立的工作流，专门用于生成、评审和保存测试用例。
    它与 multimodal_workflow 相互独立，通过 testcase_generation_node 适配器进行集成。

    工作流程：
    1. 节点1：编写测试用例
       - 根据 file_type 字段选择处理方式：
         * file_type="image": 从消息中提取图片 → 使用GPT-4O分析 → 生成测试用例
         * file_type="pdf": 从消息中提取PDF → 提取文本和图片 → 使用GPT-4O分析 → 生成测试用例
         * file_type="text": 使用纯文本模式 → 使用DeepSeek生成测试用例
       - 如果文件提取失败，自动降级到纯文本模式
       - 返回生成的测试用例列表

    2. 节点2：评审测试用例
       - 使用LLM自动评审生成的测试用例
       - 返回评审结果、得分和改进建议

    3. 条件边：评审决策
       - 评审通过 OR 评审次数>=3 → 保存到Excel
       - 否则 → 返回节点1重新生成

    4. 节点3：保存到Excel
       - 将测试用例和评审信息保存到Excel文件
       - 返回文件路径

    输入状态（TestCaseState）：
        - messages: 消息列表（包含文件或纯文本）
        - file_type: 文件类型（"image", "pdf", "text"）
        - extracted_content: 提取的内容（可选）
        - test_requirement: 测试需求描述
        - test_review_count: 评审次数（初始为0）

    输出状态（TestCaseState）：
        - test_cases_list: 生成的测试用例列表
        - review_passed: 评审是否通过
        - review_score: 评审得分
        - file_path: 保存的Excel文件路径

    Returns:
        编译后的工作流应用
    """
    print("\n" + "="*80)
    print("构建测试用例生成工作流...")
    print("="*80)

    # 创建状态图
    workflow = StateGraph(TestCaseState)
    
    # 添加节点
    print("\n[节点] 添加工作流节点...")
    workflow.add_node("write_test_case", write_test_case_node)
    workflow.add_node("review_test_case", review_test_case_node)
    workflow.add_node("save_to_excel", save_to_excel_node)
    
    # 添加边
    print("[边] 添加工作流边...")
    
    # START → 节点1
    workflow.add_edge(START, "write_test_case")
    
    # 节点1 → 节点2
    workflow.add_edge("write_test_case", "review_test_case")
    
    # 节点2 → 条件边 → 节点3 或 节点1
    workflow.add_conditional_edges(
        "review_test_case",
        review_decision_edge_new,
        {
            "save_to_excel": "save_to_excel",
            "write_test_case": "write_test_case"
        }
    )
    
    # 节点3 → END
    workflow.add_edge("save_to_excel", END)
    
    # 编译工作流
    print("[编译] 编译工作流...")
    app = workflow.compile()
    
    print("\n" + "="*80)
    print("✅ 测试用例生成工作流构建完成！")
    print("="*80)
    print("\n工作流结构:")
    print("START → 节点1(编写) → 节点2(评审) → 条件边(决策) → 节点3(保存) → END")
    print("                                          ↓")
    print("                                        节点1(重新生成)")
    print("\n支持的功能:")
    print("  1. 图片分析 - 使用GPT-4O多模态模型（file_type='image'）")
    print("  2. PDF分析 - 使用GPT-4O多模态模型（file_type='pdf'）")
    print("     - 提取PDF文本内容")
    print("     - 提取PDF中的图片")
    print("     - 使用GPT-4O分析图片")
    print("     - 基于完整内容生成测试用例")
    print("  3. 纯文本 - 使用DeepSeek模型（file_type='text'）")
    print("  4. AI自动评审 - 无需人工干预")
    print("  5. 自动重新生成 - 评审不通过时自动重新生成")
    print("  6. 强制保存 - 评审3次后强制保存")
    print("  7. 自动降级 - 文件提取失败时自动降级到纯文本模式")
    print("="*80 + "\n")
    
    return app


if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    # 构建工作流
    app = build_testcase_workflow()

    # 测试示例
    print("\n【测试示例】纯文本测试用例生成")
    print("-" * 80)

    initial_state = TestCaseState(
        messages=[HumanMessage(content="请为用户登录功能编写测试用例")],
        file_type="text",
        extracted_content="",
        test_requirement="请为用户登录功能编写测试用例，包括正常登录、错误密码、用户不存在等场景",
        test_review_count=0
    )
    
    print(f"\n[输入] 需求: {initial_state['test_requirement']}")
    print(f"[输入] 文件类型: {initial_state['file_type']}")
    
    # 执行工作流
    print("\n[执行] 启动工作流...")
    result = app.invoke(initial_state)
    
    print("\n" + "="*80)
    print("✅ 工作流执行完成！")
    print("="*80)
    
    # 输出结果
    print(f"\n[结果] 生成的测试用例数量: {len(result.get('test_cases_list', []))}")
    print(f"[结果] 评审通过: {result.get('review_passed', False)}")
    print(f"[结果] 评审得分: {result.get('review_score', 0)}/100")
    print(f"[结果] 保存文件: {result.get('file_path', '未保存')}")

