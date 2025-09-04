from typing import Any, Callable, Dict, Literal, Optional, Self, Sequence, Union

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils import from_env, secret_from_env
import openai
from pydantic import Field, SecretStr, model_validator

from .base_model import BaseChatOpenAILikeModel

enable_streaming_model = [
    "qwen3-235b-a22b",
    "qwen3-32b",
    "qwen3-30b-a3b",
    "qwen3-14b",
    "qwen3-8b",
    "qwen3-4b",
    "qwen3-1.7b",
    "qwen3-0.6b",
    "qwq-32b",
    "qwq-plus",
    "qwq-plus-latest",
    "qvq-max",
    "qvq-max-latest",
    "qvq-plus",
    "qvq-plus-latest",
]


support_tool_choice_models = [
    "qwen3-235b-a22b-instruct-2507",
    "qwen3-30b-a3b-instruct-2507",
    "qwen3-coder-480b-a35b-instruct",
    "qwen3-coder-plus",
    "qwen3-coder-30b-a3b-instruct",
    "qwen-max",
    "qwen-max-latest",
    "qwen-plus",
    "qwen-plus-latest",
    "qwen-turbo",
    "qwen-turbo-latest",
    "qwen3-235b-a22b",
    "qwen3-32b",
    "qwen3-30b-a3b",
    "qwen3-14b",
    "qwen3-8b",
    "qwen3-4b",
    "qwen3-1.7b",
    "qwen3-0.6b",
    "qwen2.5-14b-instruct-1m",
    "qwen2.5-7b-instruct-1m",
    "qwen2.5-72b-instruct",
    "qwen2.5-32b-instruct",
    "qwen2.5-14b-instruct",
    "qwen2.5-7b-instruct",
    "qwen2.5-3b-instruct",
    "qwen2.5-1.5b-instruct",
    "qwen2.5-0.5b-instruct",
]


class ChatDashScopeModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="qwen-flash")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("DASHSCOPE_API_KEY", default=None),
    )
    api_base: str = Field(
        default_factory=from_env(
            "DASHSCOPE_API_BASE",
            default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-dashscope-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "DASHSCOPE_API_KEY"}

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        if self.api_base and not (self.api_key and self.api_key.get_secret_value()):
            raise ValueError(
                "If using default api base, DASHSCOPE_API_KEY must be set."
            )
        client_params: dict = {
            k: v
            for k, v in {
                "api_key": self.api_key.get_secret_value() if self.api_key else None,
                "base_url": self.api_base,
                "timeout": self.request_timeout,
                "max_retries": self.max_retries,
                "default_headers": self.default_headers,
                "default_query": self.default_query,
            }.items()
            if v is not None
        }

        if not (self.client or None):  # type: ignore
            sync_specific: dict = {"http_client": self.http_client}
            self.root_client = openai.OpenAI(**client_params, **sync_specific)
            self.client = self.root_client.chat.completions
        if not (self.async_client or None):  # type: ignore
            async_specific: dict = {"http_client": self.http_async_client}
            self.root_async_client = openai.AsyncOpenAI(
                **client_params,
                **async_specific,
            )
            self.async_client = self.root_async_client.chat.completions

        model = self.model_name

        if (
            model in enable_streaming_model and self.enable_thinking is not False
        ) or self.enable_thinking:
            self.streaming = True
        return self

    @property
    def _default_params(self) -> Dict[str, Any]:
        if self.enable_thinking is not None:
            if self.extra_body is None:
                self.extra_body = {"enable_thinking": self.enable_thinking}
            else:
                self.extra_body = {
                    **self.extra_body,
                    "enable_thinking": self.enable_thinking,
                }

        if self.thinking_budget is not None:
            if self.extra_body is None:
                self.extra_body = {"thinking_budget": self.thinking_budget}
            else:
                self.extra_body = {
                    **self.extra_body,
                    "thinking_budget": self.thinking_budget,
                }

        return super()._default_params

    def _check_support_tool_choice(self):
        if self.model_name in support_tool_choice_models:
            if (
                self.model_name.startswith("qwen3")
                and "instruct" not in self.model_name
            ) or self.enable_thinking:
                self.enable_thinking = False
            return True
        return False

    def bind_tools(
        self,
        tools: Sequence[Union[dict[str, Any], type, Callable, BaseTool]],
        *,
        tool_choice: Optional[
            Union[dict, str, Literal["auto", "none", "required", "any"], bool]
        ] = None,
        strict: Optional[bool] = None,
        parallel_tool_calls: Optional[bool] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        if parallel_tool_calls is None:
            parallel_tool_calls = True
        if tool_choice == "any" or tool_choice == "required":
            tool_choice = "auto"

        return super().bind_tools(
            tools,
            tool_choice=tool_choice,
            strict=strict,
            parallel_tool_calls=parallel_tool_calls,
            **kwargs,
        )
