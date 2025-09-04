from functools import cache
from typing import (
    Any,
    Type,
    TypedDict,
)

from pydantic import (
    SecretStr,
)

from .providers.base_model import BaseChatOpenAILikeModel
from .providers import provider_types


class ChatModelExtraParams(TypedDict, total=False):
    temperature: float
    top_p: float
    presence_penalty: float
    frequency_penalty: float
    max_tokens: int
    n: int
    max_retries: int
    logprobs: bool
    top_logprobs: int
    enable_thinking: bool
    thinking_budget: int
    thinking: bool
    model_kwargs: dict[str, Any]
    disabled_params: dict[str, Any]
    api_key: SecretStr
    api_base: str


@cache
def _create_openai_like_chat_model(
    provider: provider_types,
) -> Type[BaseChatOpenAILikeModel]:
    if provider == "custom":
        from .providers.custom import ChatOpenAILIkeModel

        return ChatOpenAILIkeModel
    elif provider == "dashscope":
        from .providers.dashscope import ChatDashScopeModel

        return ChatDashScopeModel
    elif provider == "deepseek":
        from .providers.deepseek import ChatDeepSeekModel

        return ChatDeepSeekModel
    elif provider == "groq":
        from .providers.groq import ChatGroqModel

        return ChatGroqModel
    elif provider == "huggingface":
        from .providers.huggingface import ChatHuggingfaceModel

        return ChatHuggingfaceModel
    elif provider == "moonshot":
        from .providers.moonshot import ChatMoonshotModel

        return ChatMoonshotModel
    elif provider == "ollama":
        from .providers.ollama import ChatOllamaModel

        return ChatOllamaModel
    elif provider == "openrouter":
        from .providers.openrouter import ChatOpenRouterModel

        return ChatOpenRouterModel
    elif provider == "siliconflow":
        from .providers.siliconflow import ChatSiliconFlowModel

        return ChatSiliconFlowModel
    elif provider == "vllm":
        from .providers.vllm import ChatVLLMModel

        return ChatVLLMModel
    elif provider == "zai":
        from .providers.zai import ChatZAIModel

        return ChatZAIModel
    else:
        raise ValueError(f"Unknown provider: {provider}")
