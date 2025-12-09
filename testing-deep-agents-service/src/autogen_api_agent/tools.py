import json
from typing import Any

from langchain.tools import tool
from langchain_core.messages import AIMessage

from core.llms import deepseek_model
from .prompts import API_SPEC_PROMPT, API_TEST_PROMPT


def _to_text(response: Any) -> str:
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


def _to_json(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    try:
        obj = json.loads(text)
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "invalid-json", "raw": text}, ensure_ascii=False)


@tool
def design_api_spec(requirement_or_doc: str) -> str:
    """根据业务需求/接口描述生成结构化 API 规范。"""
    resp = deepseek_model.invoke(
        [
            {"role": "system", "content": API_SPEC_PROMPT},
            {"role": "user", "content": requirement_or_doc},
        ]
    )
    return _to_json(_to_text(resp))


@tool
def generate_api_test_plan(api_spec_json: str) -> str:
    """基于 API 规范 JSON 生成测试计划与自动化建议。"""
    resp = deepseek_model.invoke(
        [
            {"role": "system", "content": API_TEST_PROMPT},
            {"role": "user", "content": api_spec_json},
        ]
    )
    return _to_json(_to_text(resp))
