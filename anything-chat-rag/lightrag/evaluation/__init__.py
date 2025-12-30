"""
LightRAG Evaluation Module

RAGAS-based evaluation framework for assessing RAG system quality.

Usage:
    from lightrag.evaluation import RAGEvaluator

    evaluator = RAGEvaluator()
    results = await evaluator.run()

Note: RAGEvaluator is imported lazily to avoid import errors
when ragas/datasets are not installed.
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRBd2VRPT06NjE1NjIxZjk=

__all__ = ["RAGEvaluator"]


def __getattr__(name):
    """Lazy import to avoid dependency errors when ragas is not installed."""
    if name == "RAGEvaluator":
        from .eval_rag_quality import RAGEvaluator
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRBd2VRPT06NjE1NjIxZjk=

        return RAGEvaluator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
