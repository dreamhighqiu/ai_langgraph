import json
from typing import Any

from langchain.tools import tool
from langchain_core.messages import AIMessage

from core.llms import deepseek_model
from .prompts import REQUIREMENT_ANALYZER_PROMPT, TESTCASE_GENERATOR_PROMPT


def _extract_text(response: Any) -> str:
    if isinstance(response, str):
        return response
    if isinstance(response, AIMessage):
        content = response.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    if hasattr(response, "content"):
        content = getattr(response, "content")
        if isinstance(content, str):
            return content
    return str(response)


def _ensure_json(text: str) -> str:
    text = text.strip()
    # 尝试截取第一个 { 开始到最后一个 }
    if not text.startswith("{"):
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
def analyze_requirement_document(document: str) -> str:
    """将需求文档转成结构化需求 JSON。"""
    messages = [
        {"role": "system", "content": REQUIREMENT_ANALYZER_PROMPT},
        {"role": "user", "content": document},
    ]
    response = deepseek_model.invoke(messages)
    return _ensure_json(_extract_text(response))


@tool
def generate_testcases_from_requirements(requirements_json: str) -> str:
    """根据结构化需求（JSON 字符串）生成测试用例 JSON。"""
    try:
        json.loads(requirements_json)
    except json.JSONDecodeError:
        return json.dumps(
            {"error": "invalid-requirements-json", "raw": requirements_json},
            ensure_ascii=False,
        )
    messages = [
        {"role": "system", "content": TESTCASE_GENERATOR_PROMPT},
        {"role": "user", "content": requirements_json},
    ]
    response = deepseek_model.invoke(messages)
    return _ensure_json(_extract_text(response))
