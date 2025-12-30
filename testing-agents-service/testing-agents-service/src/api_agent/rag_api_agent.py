"""
API自动化测试Agent主入口

基于DeepAgents框架的智能API自动化测试系统。
支持灵活的工作流程：
- 仅生成测试计划
- 仅生成测试脚本
- 执行测试
- 完整的自动化测试流程

使用方式：
    # 交互模式
    python -m api_agent.rag_api_agent

    # 指定API文档
    python -m api_agent.rag_api_agent --api-doc swagger.json

    # 仅生成测试计划
    python -m api_agent.rag_api_agent --api-doc swagger.json --task plan

    # 生成并执行测试
    python -m api_agent.rag_api_agent --api-doc swagger.json --task full --parallel 4
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmpaalF3PT06ZTc5MWI5N2Y=

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
# fmt: off  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmpaalF3PT06ZTc5MWI5N2Y=

from api_agent.core.config import AgentConfig, get_config
from api_agent.core.orchestrator import APITestOrchestrator
#
#
# # 配置日志
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)
#
#
# # ============================================================================
# # 交互模式
# # ============================================================================
#
# async def run_interactive_mode(config: AgentConfig):
#     """
#     运行交互模式
#
#     用户可以通过命令行与Agent进行对话。
#     """
#     print("\n" + "=" * 60)
#     print("🤖 API自动化测试Agent")
#     print("=" * 60)
#     print("欢迎使用API自动化测试Agent！")
#     print("您可以：")
#     print("  - 提供API文档让我分析并生成测试计划")
#     print("  - 要求生成pytest测试脚本")
#     print("  - 执行测试并查看结果")
#     print("  - 分析测试失败原因")
#     print("\n输入 'quit' 或 'exit' 退出")
#     print("-" * 60 + "\n")
#
#     async with APITestOrchestrator(config=config, debug=False) as orchestrator:
#         while True:
#             try:
#                 user_input = input("👤 您: ").strip()
#
#                 if not user_input:
#                     continue
#
#                 if user_input.lower() in ['quit', 'exit', 'q']:
#                     print("\n👋 再见！")
#                     break
#
#                 print("\n🤖 Agent: 正在处理...\n")
#
#                 result = await orchestrator.run(user_input)
#
#                 # 提取最后一条消息
#                 messages = result.get("messages", [])
#                 if messages:
#                     last_message = messages[-1]
#                     if hasattr(last_message, 'content'):
#                         print(f"🤖 Agent: {last_message.content}\n")
#                     else:
#                         print(f"🤖 Agent: {last_message}\n")
#
#             except KeyboardInterrupt:
#                 print("\n\n👋 再见！")
#                 break
#             except Exception as e:
#                 logger.error(f"处理请求时出错: {e}")
#                 print(f"\n❌ 错误: {e}\n")
#
#
# # ============================================================================
# # 任务模式
# # ============================================================================
#
# async def run_task_mode(
#     config: AgentConfig,
#     api_doc_path: str,
#     task: str,
#     output_dir: Optional[str] = None,
#     parallel: int = 0,
# ):
#     """
#     运行任务模式
#
#     根据指定的任务类型执行相应的操作。
#
#     Args:
#         config: Agent配置
#         api_doc_path: API文档路径
#         task: 任务类型 (plan/generate/execute/full)
#         output_dir: 输出目录
#         parallel: 并行执行的worker数量
#     """
#     # 读取API文档
#     if not os.path.exists(api_doc_path):
#         print(f"❌ API文档不存在: {api_doc_path}")
#         return
#
#     with open(api_doc_path, 'r', encoding='utf-8') as f:
#         api_doc_content = f.read()
#
#     # 构建任务消息
#     task_messages = {
#         "plan": f"请分析以下API文档并生成详细的测试计划：\n\n{api_doc_content}",
#         "generate": f"请根据以下API文档生成pytest测试脚本（使用Allure报告）：\n\n{api_doc_content}",
#         "execute": "请执行已生成的测试脚本并生成Allure报告",
#         "full": f"请完成完整的API自动化测试流程：\n1. 分析API文档\n2. 生成测试计划\n3. 生成pytest测试脚本\n4. 执行测试\n5. 生成Allure报告\n\nAPI文档：\n{api_doc_content}"
#     }
#
#     if task not in task_messages:
#         print(f"❌ 未知任务类型: {task}")
#         print("支持的任务类型: plan, generate, execute, full")
#         return
#
#     message = task_messages[task]
#
#     # 添加并行执行参数
#     if parallel > 0 and task in ["execute", "full"]:
#         message += f"\n\n请使用 {parallel} 个worker并行执行测试。"
#
#     # 添加输出目录
#     if output_dir:
#         message += f"\n\n输出目录: {output_dir}"
#
#     print(f"\n🚀 开始执行任务: {task}")
#     print("-" * 60)
#
#     async with APITestOrchestrator(config=config, debug=False) as orchestrator:
#         try:
#             result = await orchestrator.run(message)
#
#             messages = result.get("messages", [])
#             if messages:
#                 last_message = messages[-1]
#                 if hasattr(last_message, 'content'):
#                     print(f"\n📋 结果:\n{last_message.content}")
#                 else:
#                     print(f"\n📋 结果:\n{last_message}")
#
#             print("\n" + "=" * 60)
#             print("✅ 任务完成")
#
#         except Exception as e:
#             logger.error(f"执行任务时出错: {e}")
#             print(f"\n❌ 错误: {e}")
#
#
# # ============================================================================
# # 主入口
# # ============================================================================
#
# def main():
#     """主入口函数"""
#     import argparse
#
#     parser = argparse.ArgumentParser(
#         description="API自动化测试Agent",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# 示例:
#   # 交互模式
#   python -m api_agent.main
#
#   # 分析API文档并生成测试计划
#   python -m api_agent.main --api-doc swagger.json --task plan
#
#   # 生成pytest测试脚本
#   python -m api_agent.main --api-doc swagger.json --task generate
#
#   # 完整自动化测试（并行执行）
#   python -m api_agent.main --api-doc swagger.json --task full --parallel 4
#         """
#     )
#
#     parser.add_argument(
#         "--api-doc",
#         type=str,
#         help="API文档路径（OpenAPI/Swagger JSON或YAML）"
#     )
#
#     parser.add_argument(
#         "--task",
#         type=str,
#         choices=["plan", "generate", "execute", "full"],
#         default="full",
#         help="任务类型: plan(测试计划), generate(生成脚本), execute(执行测试), full(完整流程)"
#     )
#
#     parser.add_argument(
#         "--output-dir",
#         type=str,
#         help="输出目录"
#     )
#
#     parser.add_argument(
#         "--parallel",
#         type=int,
#         default=0,
#         help="并行执行的worker数量（0=自动检测）"
#     )
#
#     parser.add_argument(
#         "--model",
#         type=str,
#         default="deepseek-chat",
#         help="LLM模型名称"
#     )
#
#     parser.add_argument(
#         "--debug",
#         action="store_true",
#         help="启用调试模式"
#     )
#
#     args = parser.parse_args()
#
#     # 配置日志级别
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)
#
#     # 获取配置
#     config = get_config()
#
#     # 覆盖模型配置
#     if args.model:
#         config.llm.model_name = args.model
#
#     # 覆盖输出目录
#     if args.output_dir:
#         config.test_execution.output_dir = args.output_dir
#
#     # 运行
#     if args.api_doc:
#         # 任务模式
#         asyncio.run(run_task_mode(
#             config=config,
#             api_doc_path=args.api_doc,
#             task=args.task,
#             output_dir=args.output_dir,
#             parallel=args.parallel
#         ))
#     else:
#         # 交互模式
#         asyncio.run(run_interactive_mode(config))
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmpaalF3PT06ZTc5MWI5N2Y=

api = APITestOrchestrator()
asyncio.run(api.initialize())

agent = api.agent
# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmpaalF3PT06ZTc5MWI5N2Y=

#
# if __name__ == "__main__":
#     main()