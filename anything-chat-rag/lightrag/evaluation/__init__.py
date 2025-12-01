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


# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRBd2VRPT06NjE1NjIxZjk=

__all__ = ["RAGEvaluator"]


def __getattr__(name):
    """Lazy import to avoid dependency errors when ragas is not installed."""
    if name == "RAGEvaluator":
        from .eval_rag_quality import RAGEvaluator
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRBd2VRPT06NjE1NjIxZjk=

        return RAGEvaluator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
