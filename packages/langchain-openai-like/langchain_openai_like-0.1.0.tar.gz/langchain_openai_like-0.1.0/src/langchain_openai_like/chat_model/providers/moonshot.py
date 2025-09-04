from typing import Any, Callable, Dict, Literal, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils import from_env, secret_from_env
from pydantic import Field, SecretStr

from .base_model import BaseChatOpenAILikeModel


class ChatMoonshotModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="kimi-k2-0711-preview")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("MOONSHOT_API_KEY", default=None),
    )
    api_base: str = Field(
        default_factory=from_env(
            "MOONSHOT_API_BASE",
            default="https://api.moonshot.cn/v1",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-moonshot-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "MOONSHOT_API_KEY"}

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
        if tool_choice == "any" or tool_choice == "required":
            tool_choice = "auto"

        return super().bind_tools(
            tools,
            tool_choice=tool_choice,
            strict=strict,
            parallel_tool_calls=parallel_tool_calls,
            **kwargs,
        )
