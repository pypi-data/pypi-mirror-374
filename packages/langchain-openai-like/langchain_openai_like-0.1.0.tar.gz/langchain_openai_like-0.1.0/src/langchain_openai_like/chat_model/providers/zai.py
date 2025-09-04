from typing import Any, Callable, Dict, Literal, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils import from_env, secret_from_env
from pydantic import Field, SecretStr

from .base_model import BaseChatOpenAILikeModel


class ChatZAIModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="glm-4.5-air")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("ZAI_API_KEY", default=None),
    )
    api_base: str = Field(
        default_factory=from_env(
            "ZAI_API_BASE",
            default="https://open.bigmodel.cn/api/paas/v4",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-zai-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "ZAI_API_KEY"}

    @property
    def _default_params(self) -> Dict[str, Any]:
        if self.thinking is not None:
            if self.extra_body is None:
                self.extra_body = {
                    "thinking": {"type": "enabled" if self.thinking else "disabled"}
                }
            else:
                self.extra_body = {
                    **self.extra_body,
                    "thinking": {"type": "enabled" if self.thinking else "disabled"},
                }

        return super()._default_params

    def _check_support_tool_choice(self) -> bool:
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
        if tool_choice != "auto":
            tool_choice = "auto"

        return super().bind_tools(
            tools,
            tool_choice=tool_choice,
            strict=strict,
            parallel_tool_calls=parallel_tool_calls,
            **kwargs,
        )
