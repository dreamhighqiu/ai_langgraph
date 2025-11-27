"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import copy
import os
from functools import lru_cache

import pipmaster as pm  # Pipmaster for dynamic library install

# install specific modules
if not pm.is_installed("transformers"):
    pm.install("transformers")
if not pm.is_installed("torch"):
    pm.install("torch")
if not pm.is_installed("numpy"):
    pm.install("numpy")

from transformers import AutoTokenizer, AutoModelForCausalLM
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from lightrag.exceptions import (
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)
import torch
import numpy as np
from lightrag.utils import wrap_embedding_func_with_attrs

os.environ["TOKENIZERS_PARALLELISM"] = "false"
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YWxFeWFnPT06YTIzOWE5M2M=


@lru_cache(maxsize=1)
def initialize_hf_model(model_name):
    hf_tokenizer = AutoTokenizer.from_pretrained(
        model_name, device_map="auto", trust_remote_code=True
    )
    hf_model = AutoModelForCausalLM.from_pretrained(
        model_name, device_map="auto", trust_remote_code=True
    )
    if hf_tokenizer.pad_token is None:
        hf_tokenizer.pad_token = hf_tokenizer.eos_token

    return hf_model, hf_tokenizer


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError)
    ),
)
async def hf_model_if_cache(
    model,
    prompt,
    system_prompt=None,
    history_messages=[],
    enable_cot: bool = False,
    **kwargs,
) -> str:
    if enable_cot:
        from lightrag.utils import logger
# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YWxFeWFnPT06YTIzOWE5M2M=

        logger.debug(
            "enable_cot=True is not supported for Hugging Face local models and will be ignored."
        )
    model_name = model
    hf_model, hf_tokenizer = initialize_hf_model(model_name)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    kwargs.pop("hashing_kv", None)
    input_prompt = ""
    try:
        input_prompt = hf_tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        try:
            ori_message = copy.deepcopy(messages)
            if messages[0]["role"] == "system":
                messages[1]["content"] = (
                    "<system>"
                    + messages[0]["content"]
                    + "</system>\n"
                    + messages[1]["content"]
                )
                messages = messages[1:]
                input_prompt = hf_tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
        except Exception:
            len_message = len(ori_message)
            for msgid in range(len_message):
                input_prompt = (
                    input_prompt
                    + "<"
                    + ori_message[msgid]["role"]
                    + ">"
                    + ori_message[msgid]["content"]
                    + "</"
                    + ori_message[msgid]["role"]
                    + ">\n"
                )

    input_ids = hf_tokenizer(
        input_prompt, return_tensors="pt", padding=True, truncation=True
    ).to("cuda")
    inputs = {k: v.to(hf_model.device) for k, v in input_ids.items()}
    output = hf_model.generate(
        **input_ids, max_new_tokens=512, num_return_sequences=1, early_stopping=True
    )
    response_text = hf_tokenizer.decode(
        output[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True
    )

    return response_text
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YWxFeWFnPT06YTIzOWE5M2M=


async def hf_model_complete(
    prompt,
    system_prompt=None,
    history_messages=[],
    keyword_extraction=False,
    enable_cot: bool = False,
    **kwargs,
) -> str:
    kwargs.pop("keyword_extraction", None)
    model_name = kwargs["hashing_kv"].global_config["llm_model_name"]
    result = await hf_model_if_cache(
        model_name,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        enable_cot=enable_cot,
        **kwargs,
    )
    return result


@wrap_embedding_func_with_attrs(embedding_dim=1024, max_token_size=8192)
async def hf_embed(texts: list[str], tokenizer, embed_model) -> np.ndarray:
    # Detect the appropriate device
    if torch.cuda.is_available():
        device = next(embed_model.parameters()).device  # Use CUDA if available
    elif torch.backends.mps.is_available():
        device = torch.device("mps")  # Use MPS for Apple Silicon
    else:
        device = torch.device("cpu")  # Fallback to CPU
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YWxFeWFnPT06YTIzOWE5M2M=

    # Move the model to the detected device
    embed_model = embed_model.to(device)

    # Tokenize the input texts and move them to the same device
    encoded_texts = tokenizer(
        texts, return_tensors="pt", padding=True, truncation=True
    ).to(device)

    # Perform inference
    with torch.no_grad():
        outputs = embed_model(
            input_ids=encoded_texts["input_ids"],
            attention_mask=encoded_texts["attention_mask"],
        )
        embeddings = outputs.last_hidden_state.mean(dim=1)

    # Convert embeddings to NumPy
    if embeddings.dtype == torch.bfloat16:
        return embeddings.detach().to(torch.float32).cpu().numpy()
    else:
        return embeddings.detach().cpu().numpy()
