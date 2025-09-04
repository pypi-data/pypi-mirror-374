import os
from typing import Any, Optional, cast

from typing import Literal

from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import init_embeddings


provider_emb_list = Literal[
    "custom",
    "dashscope",
    "ollama",
    "vllm",
    "siliconflow",
    "zai",
]


def init_openai_like_embeddings(
    model: str,
    provider: provider_emb_list,
    dimensions: Optional[int] = None,
    chunk_size: Optional[int] = None,
    max_retries: Optional[int] = None,
    model_kwargs: Optional[dict[str, Any]] = None,
):
    return _init_openai_like_embeddings__(
        model, provider, dimensions, chunk_size, max_retries, model_kwargs
    )


def _init_openai_like_embeddings__(
    model: str,
    provider: provider_emb_list,
    dimensions: Optional[int] = None,
    chunk_size: Optional[int] = None,
    max_retries: Optional[int] = None,
    model_kwargs: Optional[dict[str, Any]] = None,
) -> OpenAIEmbeddings:
    """Get an instance of an embedding model that is compatible with the OpenAI API.
    Args:
        model: The model to use.
        provider: The provider to use.
        dimensions: The dimensions of the embedding.
        chunk_size: The size of the chunk to use when embedding.
        max_retries: The maximum number of retries to use when embedding.
        model_kwargs: Extra params to pass to the model.
    Returns:
        An instance of an embedding model that is compatible with the OpenAI API.
    """
    model_kwargs = model_kwargs or {}
    model_kwargs.update({"check_embedding_ctx_length": False})
    if max_retries:
        model_kwargs["max_retries"] = max_retries
    if dimensions:
        model_kwargs["dimensions"] = dimensions
    if chunk_size:
        model_kwargs["chunk_size"] = chunk_size

    if provider == "custom":
        if "base_url" not in model_kwargs:
            raise ValueError("base_url is required for custom provider")
        if "api_key" not in model_kwargs:
            raise ValueError("api_key is required for custom provider")
    elif provider == "dashscope":
        if "api_key" not in model_kwargs:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("api_key is required for dashscope provider")
            model_kwargs["api_key"] = api_key
        model_kwargs["base_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    elif provider == "ollama":
        model_kwargs["base_url"] = "http://localhost:11434/v1"
        model_kwargs["api_key"] = os.getenv("OLLAMA_API_KEY") or "sk-ollama"
    elif provider == "vllm":
        model_kwargs["base_url"] = "http://localhost:8000/v1"
        model_kwargs["api_key"] = os.getenv("VLLM_API_KEY") or "sk-vllm"
    elif provider == "siliconflow":
        if "api_key" not in model_kwargs:
            api_key = os.getenv("SILICONFLOW_API_KEY")
            if not api_key:
                raise ValueError("api_key is required for siliconflow provider")
            model_kwargs["api_key"] = api_key
        model_kwargs["base_url"] = "https://api.siliconflow.cn/v1"
    elif provider == "zai":
        if "api_key" not in model_kwargs:
            api_key = os.getenv("ZAI_API_KEY")
            if not api_key:
                raise ValueError("api_key is required for zai provider")
            model_kwargs["api_key"] = api_key
        model_kwargs["base_url"] = "https://open.bigmodel.cn/api/paas/v4"

    embbeding_model = init_embeddings(model=model, provider="openai", **model_kwargs)

    return cast(OpenAIEmbeddings, embbeding_model)
