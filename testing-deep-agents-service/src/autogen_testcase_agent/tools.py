import json
from typing import Any

from langchain.tools import tool
from langchain_core.messages import AIMessage

from core.llms import deepseek_model
from .prompts import TESTCASE_EXPANSION_PROMPT, TESTCASE_REVIEW_PROMPT


def _text(response: Any) -> str:
    if isinstance(response, str):
        return response
    if isinstance(response, AIMessage):
        content = response.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    if hasattr(response, "content"):
        return str(getattr(response, "content"))
    return str(response)


def _sanitize_json(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "invalid-json", "raw": text}, ensure_ascii=False)


@tool
def expand_testcases_from_requirements(requirements_json: str) -> str:
    """根据需求 JSON 生成完整的测试用例集，输出 JSON。"""
    messages = [
        {"role": "system", "content": TESTCASE_EXPANSION_PROMPT},
        {"role": "user", "content": requirements_json},
    ]
    resp = deepseek_model.invoke(messages)
    return _sanitize_json(_text(resp))


@tool
def review_testcases(testcases_json: str) -> str:
    """评审测试用例的覆盖度与质量，输出评审 JSON。"""
    messages = [
        {"role": "system", "content": TESTCASE_REVIEW_PROMPT},
        {"role": "user", "content": testcases_json},
    ]
    resp = deepseek_model.invoke(messages)
    return _sanitize_json(_text(resp))
