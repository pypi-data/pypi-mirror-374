from __future__ import annotations

from typing import (
    Optional,
    cast,
)

from langchain_openai_like.chat_model.providers import provider_types


from .adapters import (
    ChatModelExtraParams,
    BaseChatOpenAILikeModel,
    _create_openai_like_chat_model,
)


def init_openai_like_chat_model(
    model: str,
    *,
    provider: Optional[provider_types] = None,
    model_kwargs: Optional[ChatModelExtraParams] = None,
) -> BaseChatOpenAILikeModel:
    """
    Get an instance of a chat model that is compatible with the OpenAI API.

    Args:
        model: The model to use.
        provider: The provider to use.
        model_kwargs: Extra params to pass to the model.
    Returns:
        An instance of a chat model that is compatible with the OpenAI API.
    """
    return _init_openai_like_llm_helper(
        model=model,
        provider=provider,
        model_kwargs=model_kwargs,
    )


def _get_provider_with_model(model: str) -> provider_types:
    if "deepseek" in model.lower():
        return "deepseek"
    elif "qwen" in model.lower():
        return "dashscope"
    elif "moonshot" in model.lower():
        return "moonshot"
    elif "kimi" in model.lower() or "moonshot" in model.lower():
        return "moonshot"
    elif "glm" in model.lower():
        return "zai"
    else:
        raise ValueError(f"Unknown model: {model} for provider,you must set provider")


def _init_openai_like_llm_helper(
    model: str,
    *,
    provider: Optional[provider_types] = None,
    model_kwargs: Optional[ChatModelExtraParams] = None,
) -> BaseChatOpenAILikeModel:
    if provider is None:
        if "/" in model:
            provider, model = (
                cast(provider_types, model.split("/")[0]),
                model.split("/")[1],
            )
        else:
            provider = _get_provider_with_model(model)

    model_kwargs = model_kwargs or {}

    chat_model = _create_openai_like_chat_model(provider)

    return chat_model(
        model=model,
        **model_kwargs,
    )
