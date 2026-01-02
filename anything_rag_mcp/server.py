"""
FastMCP server that wraps LightRAG's document and query HTTP endpoints.
"""

import argparse
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP, Context


def _format_json(data: Any) -> str:
    """Pretty-print JSON payloads."""
    return json.dumps(data, ensure_ascii=False, indent=2)


async def _execute_request(coro: Awaitable[Any]) -> str:
    """Run a client coroutine and format the result, capturing errors."""
    try:
        result = await coro
        return _format_json(result)
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error: {exc}"


class LightRAGClient:
    """Thin async HTTP client for the LightRAG API."""

    def __init__(self, base_url: str, api_key: Optional[str], timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"Accept": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
            )
        return self._client

    def _auth_params(self) -> Dict[str, str]:
        return {"api_key_header_value": self.api_key} if self.api_key else {}

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Any] = None,
        files: Optional[Any] = None,
    ) -> Any:
        client = await self._get_client()
        req_params: Dict[str, Any] = {}
        req_params.update(self._auth_params())
        if params:
            req_params.update(params)

        try:
            response = await client.request(
                method,
                path,
                params=req_params,
                json=json_body,
                files=files,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(
                f"HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Request failed: {exc}") from exc

    async def upload_file(self, file_path: str) -> Any:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        with path.open("rb") as file_handle:
            files = {"file": (path.name, file_handle, "application/octet-stream")}
            return await self._request("POST", "/documents/upload", files=files)

    async def insert_text(self, text: str, file_source: Optional[str]) -> Any:
        payload: Dict[str, Any] = {"text": text}
        if file_source:
            payload["file_source"] = file_source
        return await self._request("POST", "/documents/text", json_body=payload)

    async def insert_texts(self, texts: List[str], file_sources: Optional[List[str]]) -> Any:
        payload: Dict[str, Any] = {"texts": texts}
        if file_sources:
            payload["file_sources"] = file_sources
        return await self._request("POST", "/documents/texts", json_body=payload)

    async def list_documents(
        self,
        status_filter: Optional[str],
        page: int,
        page_size: int,
        sort_field: str,
        sort_direction: str,
    ) -> Any:
        body: Dict[str, Any] = {
            "status_filter": status_filter,
            "page": page,
            "page_size": page_size,
            "sort_field": sort_field,
            "sort_direction": sort_direction,
        }
        return await self._request("POST", "/documents/paginated", json_body=body)

    async def pipeline_status(self) -> Any:
        return await self._request("GET", "/documents/pipeline_status")

    async def status_counts(self) -> Any:
        return await self._request("GET", "/documents/status_counts")

    async def track_status(self, track_id: str) -> Any:
        return await self._request("GET", f"/documents/track_status/{track_id}")

    async def scan(self) -> Any:
        return await self._request("POST", "/documents/scan")

    async def reprocess_failed(self) -> Any:
        return await self._request("POST", "/documents/reprocess_failed")

    async def clear_documents(self) -> Any:
        return await self._request("DELETE", "/documents")

    async def clear_cache(self) -> Any:
        return await self._request("POST", "/documents/clear_cache", json_body={})

    async def delete_documents(
        self,
        doc_ids: List[str],
        delete_file: bool,
        delete_llm_cache: bool,
    ) -> Any:
        body = {
            "doc_ids": doc_ids,
            "delete_file": delete_file,
            "delete_llm_cache": delete_llm_cache,
        }
        return await self._request("DELETE", "/documents/delete_document", json_body=body)

    async def query(self, payload: Dict[str, Any]) -> Any:
        return await self._request("POST", "/query", json_body=payload)

    async def query_data(self, payload: Dict[str, Any]) -> Any:
        return await self._request("POST", "/query/data", json_body=payload)


class MCPContext:
    """Shared MCP context."""

    def __init__(self, client: LightRAGClient) -> None:
        self.client = client


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:
    config = server.config
    client = LightRAGClient(
        base_url=config.get("base_url", "http://127.0.0.1:9621"),
        api_key=config.get("api_key"),
        timeout=config.get("timeout", 60.0),
    )
    try:
        yield MCPContext(client)
    finally:
        await client.close()


mcp = FastMCP(name="anything-rag-mcp", lifespan=server_lifespan)


@mcp.tool()
async def upload_document(file_path: str, ctx: Context = None) -> str:
    """
    Upload a file to /documents/upload and kick off indexing.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.upload_file(file_path))


@mcp.tool()
async def insert_text_document(text: str, file_source: Optional[str] = None, ctx: Context = None) -> str:
    """
    Insert a single text document via /documents/text.
    """
    client = ctx.request_context.lifespan_context.client
    if not text or len(text.strip()) < 1:
        return "Text content is required."
    return await _execute_request(client.insert_text(text=text, file_source=file_source))


@mcp.tool()
async def insert_texts_document(
    texts: List[str],
    file_sources: Optional[List[str]] = None,
    ctx: Context = None,
) -> str:
    """
    Insert multiple text documents via /documents/texts.
    """
    client = ctx.request_context.lifespan_context.client
    if not texts:
        return "texts must contain at least one item."
    return await _execute_request(client.insert_texts(texts=texts, file_sources=file_sources))


@mcp.tool()
async def list_documents_paginated(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    sort_field: str = "updated_at",
    sort_direction: str = "desc",
    ctx: Context = None,
) -> str:
    """
    List documents with pagination via /documents/paginated.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(
        client.list_documents(status_filter, page, page_size, sort_field, sort_direction)
    )


@mcp.tool()
async def get_pipeline_status(ctx: Context = None) -> str:
    """
    Get document pipeline status.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.pipeline_status())


@mcp.tool()
async def get_status_counts(ctx: Context = None) -> str:
    """
    Get document status counts.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.status_counts())


@mcp.tool()
async def track_document(track_id: str, ctx: Context = None) -> str:
    """
    Track processing status for a given track_id.
    """
    client = ctx.request_context.lifespan_context.client
    if not track_id:
        return "track_id is required."
    return await _execute_request(client.track_status(track_id))


@mcp.tool()
async def scan_documents(ctx: Context = None) -> str:
    """
    Trigger /documents/scan to detect new files.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.scan())


@mcp.tool()
async def reprocess_failed_documents(ctx: Context = None) -> str:
    """
    Trigger reprocessing for failed/pending documents.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.reprocess_failed())


@mcp.tool()
async def clear_all_documents(ctx: Context = None) -> str:
    """
    Clear all documents and associated storage.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.clear_documents())


@mcp.tool()
async def clear_llm_cache(ctx: Context = None) -> str:
    """
    Clear cached LLM responses via /documents/clear_cache.
    """
    client = ctx.request_context.lifespan_context.client
    return await _execute_request(client.clear_cache())


@mcp.tool()
async def delete_documents(
    doc_ids: List[str],
    delete_file: bool = False,
    delete_llm_cache: bool = False,
    ctx: Context = None,
) -> str:
    """
    Delete documents by id and optionally remove files and cache.
    """
    client = ctx.request_context.lifespan_context.client
    if not doc_ids:
        return "doc_ids must contain at least one id."
    return await _execute_request(client.delete_documents(doc_ids, delete_file, delete_llm_cache))


def _build_query_payload(
    query: str,
    mode: str,
    top_k: Optional[int],
    chunk_top_k: Optional[int],
    response_type: Optional[str],
    max_entity_tokens: Optional[int],
    max_relation_tokens: Optional[int],
    max_total_tokens: Optional[int],
    hl_keywords: Optional[List[str]],
    ll_keywords: Optional[List[str]],
    conversation_history_json: Optional[str],
    user_prompt: Optional[str],
    enable_rerank: bool,
    include_references: bool,
    include_chunk_content: bool,
    only_need_context: bool,
    only_need_prompt: bool,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "query": query,
        "mode": mode,
        "enable_rerank": enable_rerank,
        "include_references": include_references,
        "include_chunk_content": include_chunk_content,
        "only_need_context": only_need_context,
        "only_need_prompt": only_need_prompt,
    }
    if top_k is not None:
        payload["top_k"] = top_k
    if chunk_top_k is not None:
        payload["chunk_top_k"] = chunk_top_k
    if response_type:
        payload["response_type"] = response_type
    if max_entity_tokens is not None:
        payload["max_entity_tokens"] = max_entity_tokens
    if max_relation_tokens is not None:
        payload["max_relation_tokens"] = max_relation_tokens
    if max_total_tokens is not None:
        payload["max_total_tokens"] = max_total_tokens
    if hl_keywords:
        payload["hl_keywords"] = hl_keywords
    if ll_keywords:
        payload["ll_keywords"] = ll_keywords
    if user_prompt:
        payload["user_prompt"] = user_prompt
    if conversation_history_json:
        try:
            payload["conversation_history"] = json.loads(conversation_history_json)
        except json.JSONDecodeError:
            raise ValueError("conversation_history_json is not valid JSON.")
    return payload


@mcp.tool()
async def query_text(
    query: str,
    mode: str = "mix",
    top_k: Optional[int] = 10,
    chunk_top_k: Optional[int] = 5,
    response_type: Optional[str] = None,
    max_entity_tokens: Optional[int] = None,
    max_relation_tokens: Optional[int] = None,
    max_total_tokens: Optional[int] = None,
    hl_keywords: Optional[List[str]] = None,
    ll_keywords: Optional[List[str]] = None,
    conversation_history_json: Optional[str] = None,
    user_prompt: Optional[str] = None,
    enable_rerank: bool = True,
    include_references: bool = True,
    include_chunk_content: bool = False,
    only_need_context: bool = False,
    only_need_prompt: bool = False,
    ctx: Context = None,
) -> str:
    """
    Call /query for a generated answer with optional references.
    """
    client = ctx.request_context.lifespan_context.client
    if len(query.strip()) < 3:
        return "query must be at least 3 characters."

    payload = _build_query_payload(
        query=query,
        mode=mode,
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        response_type=response_type,
        max_entity_tokens=max_entity_tokens,
        max_relation_tokens=max_relation_tokens,
        max_total_tokens=max_total_tokens,
        hl_keywords=hl_keywords,
        ll_keywords=ll_keywords,
        conversation_history_json=conversation_history_json,
        user_prompt=user_prompt,
        enable_rerank=enable_rerank,
        include_references=include_references,
        include_chunk_content=include_chunk_content,
        only_need_context=only_need_context,
        only_need_prompt=only_need_prompt,
    )
    return await _execute_request(client.query(payload))


@mcp.tool()
async def query_data(
    query: str,
    mode: str = "mix",
    top_k: Optional[int] = 10,
    chunk_top_k: Optional[int] = 5,
    max_entity_tokens: Optional[int] = None,
    max_relation_tokens: Optional[int] = None,
    max_total_tokens: Optional[int] = None,
    hl_keywords: Optional[List[str]] = None,
    ll_keywords: Optional[List[str]] = None,
    conversation_history_json: Optional[str] = None,
    user_prompt: Optional[str] = None,
    enable_rerank: bool = True,
    include_references: bool = True,
    include_chunk_content: bool = True,
    only_need_context: bool = False,
    only_need_prompt: bool = False,
    ctx: Context = None,
) -> str:
    """
    Call /query/data for structured RAG response (entities, relationships, chunks, references).
    """
    client = ctx.request_context.lifespan_context.client
    if len(query.strip()) < 3:
        return "query must be at least 3 characters."

    payload = _build_query_payload(
        query=query,
        mode=mode,
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        response_type=None,
        max_entity_tokens=max_entity_tokens,
        max_relation_tokens=max_relation_tokens,
        max_total_tokens=max_total_tokens,
        hl_keywords=hl_keywords,
        ll_keywords=ll_keywords,
        conversation_history_json=conversation_history_json,
        user_prompt=user_prompt,
        enable_rerank=enable_rerank,
        include_references=include_references,
        include_chunk_content=include_chunk_content,
        only_need_context=only_need_context,
        only_need_prompt=only_need_prompt,
    )
    return await _execute_request(client.query_data(payload))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Anything RAG MCP server (LightRAG HTTP wrapper)")
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.environ.get("LIGHTRAG_BASE_URL", "http://127.0.0.1:9621"),
        help="LightRAG base URL.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("LIGHTRAG_API_KEY"),
        help="Optional API key, sent as api_key_header_value.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("LIGHTRAG_TIMEOUT", 60.0)),
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("ANYTHING_RAG_MCP_PORT", 8006)),
        help="Port for SSE transport.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("ANYTHING_RAG_MCP_HOST", "0.0.0.0"),
        help="Host for SSE transport.",
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["sse", "stdio"],
        default=os.environ.get("ANYTHING_RAG_MCP_TRANSPORT", "sse"),
        help="Transport mode (sse or stdio).",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_arguments()
    mcp.config = {
        "base_url": args.base_url,
        "api_key": args.api_key,
        "timeout": args.timeout,
    }

    if args.transport == "sse":
        mcp.run(transport="sse", port=args.port, host=args.host)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
