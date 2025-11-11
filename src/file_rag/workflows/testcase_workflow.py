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
    
    工作流程：
    1. 节点1：编写测试用例
       - 检测文件类型（图片、PDF、纯文本）
       - 选择合适的LLM模型
       - 生成测试用例
    
    2. 节点2：评审测试用例
       - 使用LLM自动评审
       - 返回评审结果和得分
    
    3. 条件边：评审决策
       - 通过 OR 次数>=3 → 保存
       - 否则 → 重新生成
    
    4. 节点3：保存到Excel
       - 添加评审信息
       - 保存到Excel文件
    
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
    print("  1. 图片分析 - 使用GPT-5多模态模型")
    print("  2. PDF分析 - 使用GPT-5多模态模型")
    print("  3. 纯文本 - 使用DeepSeek模型")
    print("  4. AI自动评审 - 无需人工干预")
    print("  5. 自动重新生成 - 评审不通过时自动重新生成")
    print("  6. 强制保存 - 评审3次后强制保存")
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

