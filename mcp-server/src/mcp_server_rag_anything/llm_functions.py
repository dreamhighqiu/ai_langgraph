"""
LLM, Vision, and Embedding Functions for RAG Anything

This module provides factory functions for creating LLM, vision, and embedding
functions compatible with the RAG Anything framework. These functions handle
communication with LightRAG and external LLM/Vision APIs.

Functions:
    _handle_coroutine_result: Handle potential coroutine return values
    create_llm_model_func: Create LLM model function factory
    create_vision_model_func: Create vision model function factory
    create_embedding_func: Create embedding function factory
"""



import asyncio
import logging
import concurrent.futures
from typing import Callable, Optional, Any

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
# 禁用 LightRAG 默认的 response_format 以兼容 deepseek 等模型
import lightrag.llm.openai as lightrag_openai
lightrag_openai.DEFAULT_RESPONSE_FORMAT = None

from .config import MCSConfig

logger = logging.getLogger(__name__)
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjBwVmRnPT06ZTI3MWRjYzU=


def _handle_coroutine_result(result: Any) -> str:
    """
    Handle potential coroutine return values from LightRAG functions.
    
    LightRAG functions may return either a string or a coroutine depending on
    the context. This function detects and properly handles both cases.
    
    When called from LightRAG's worker thread (which may have an event loop),
    we need to run the coroutine in a separate thread to avoid conflicts.

    Args:
        result: The result from LightRAG function (could be str or coroutine)

    Returns:
        str: The actual string result

    Raises:
        RuntimeError: If coroutine execution fails
    """
    if asyncio.iscoroutine(result):
        try:
            # Check if we're already in an async context
            loop = asyncio.get_running_loop()
            # If we're in an async context (LightRAG worker thread),
            # run the coroutine in a separate thread with a new event loop
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_coroutine_in_new_loop, result)
                result = future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            result = asyncio.run(result)

    return result if isinstance(result, str) else str(result)


def _run_coroutine_in_new_loop(coro):
    """Run a coroutine in a new event loop in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def create_llm_model_func(config: MCSConfig) -> Callable:
    """
    Create LLM model function for RAGAnything using OpenAI API.
    
    This factory function creates a callable that can be used by RAGAnything
    to make LLM API calls. The returned function handles:
    - API communication with configured LLM provider
    - Conversation history management
    - System prompts
    - Temperature and token limits
    - Coroutine handling
    - Error handling and logging

    Args:
        config: MCSConfig instance with LLM configuration

    Returns:
        Callable: LLM model function with signature:
            (prompt: str, system_prompt: Optional[str] = None,
             history_messages: Optional[list] = None, **kwargs) -> str

    Example:
        >>> config = MCSConfig.from_env()
        >>> llm_func = create_llm_model_func(config)
        >>> response = llm_func("What is AI?")
        >>> print(response)
    """
    def llm_model_func(
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        Call LLM API with the configured provider.

        Args:
            prompt: The main prompt/query
            system_prompt: Optional system prompt
            history_messages: Optional conversation history
            **kwargs: Additional arguments passed to the LLM

        Returns:
            str: LLM response text

        Raises:
            Exception: If LLM API call fails
        """
        if history_messages is None:
            history_messages = []

        # deepseek 不支持 OpenAI response_format，强制关闭关键词提取/response_format
        kwargs.pop("keyword_extraction", None)
        kwargs.pop("response_format", None)

        try:
            result = openai_complete_if_cache(
                config.llm.model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=config.llm.api_key,
                base_url=config.llm.base_url,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens,
                **kwargs,
            )
            return _handle_coroutine_result(result)
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise
# pragma: no cover  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjBwVmRnPT06ZTI3MWRjYzU=

    return llm_model_func


def create_vision_model_func(config: MCSConfig) -> Callable:
    """
    Create vision model function for multimodal processing.
    
    This factory function creates a callable for processing multimodal content
    including images, tables, and equations. The returned function supports:
    - Pre-formatted messages for VLM enhanced queries
    - Single image processing with base64 encoding
    - Text fallback to LLM when no images provided
    - Proper message formatting for vision models
    - Error handling and logging

    Args:
        config: MCSConfig instance with vision configuration

    Returns:
        Callable: Vision model function with signature:
            (prompt: str, system_prompt: Optional[str] = None,
             history_messages: Optional[list] = None,
             image_data: Optional[str] = None,
             messages: Optional[list] = None, **kwargs) -> str

    Example:
        >>> config = MCSConfig.from_env()
        >>> vision_func = create_vision_model_func(config)
        >>> response = vision_func("Describe this image", image_data=base64_image)
        >>> print(response)
    """
    def vision_model_func(
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: Optional[list] = None,
        image_data: Optional[str] = None,
        messages: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        Call vision model API for image/multimodal processing.

        Args:
            prompt: The main prompt/query
            system_prompt: Optional system prompt
            history_messages: Optional conversation history
            image_data: Base64 encoded image data
            messages: Pre-formatted messages for multimodal VLM
            **kwargs: Additional arguments

        Returns:
            str: Vision model response

        Raises:
            Exception: If vision model API call fails
        """
        if history_messages is None:
            history_messages = []
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjBwVmRnPT06ZTI3MWRjYzU=

        try:
            # If messages format is provided (for multimodal VLM enhanced query), use it directly
            if messages:
                result = openai_complete_if_cache(
                    config.vision.model or config.llm.model,
                    "",
                    system_prompt=None,
                    history_messages=[],
                    messages=messages,
                    api_key=config.vision.api_key or config.llm.api_key,
                    base_url=config.vision.base_url or config.llm.base_url,
                    **kwargs,
                )
                return _handle_coroutine_result(result)

            # Traditional single image format
            elif image_data:
                # Build messages list, filtering out None values
                messages_list = []
                if system_prompt:
                    messages_list.append({"role": "system", "content": system_prompt})

                messages_list.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                        },
                    ],
                })

                result = openai_complete_if_cache(
                    config.vision.model or config.llm.model,
                    "",
                    system_prompt=None,
                    history_messages=[],
                    messages=messages_list,
                    api_key=config.vision.api_key or config.llm.api_key,
                    base_url=config.vision.base_url or config.llm.base_url,
                    **kwargs,
                )
                return _handle_coroutine_result(result)

            # Pure text format - fallback to LLM
            else:
                llm_func = create_llm_model_func(config)
                return llm_func(prompt, system_prompt, history_messages, **kwargs)
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjBwVmRnPT06ZTI3MWRjYzU=

        except Exception as e:
            logger.error(f"Error calling vision model: {e}")
            raise

    return vision_model_func


def create_embedding_func(config: MCSConfig) -> EmbeddingFunc:
    """
    Create embedding function for RAGAnything.
    
    This factory function creates an embedding function wrapper that can be
    used by RAGAnything for text vectorization. The function:
    - Uses OpenAI-compatible embedding API
    - Handles configurable embedding dimensions
    - Manages token size limits
    - Provides proper error handling

    Args:
        config: MCSConfig instance with embedding configuration

    Returns:
        EmbeddingFunc: Embedding function wrapper with configured dimensions

    Raises:
        Exception: If embedding function creation fails

    Example:
        >>> config = MCSConfig.from_env()
        >>> embedding_func = create_embedding_func(config)
        >>> embeddings = embedding_func(["Hello", "World"])
    """
    try:
        embedding_func = EmbeddingFunc(
            embedding_dim=config.embedding.dimension,
            max_token_size=8192,
            func=lambda texts: openai_embed(
                texts,
                model=config.embedding.model,
                api_key=config.llm.api_key,
                base_url=config.llm.base_url,
            ),
        )
        logger.info(f"Embedding function created: {config.embedding.model} (dim={config.embedding.dimension})")
        return embedding_func
    except Exception as e:
        logger.error(f"Error creating embedding function: {e}")
        raise
