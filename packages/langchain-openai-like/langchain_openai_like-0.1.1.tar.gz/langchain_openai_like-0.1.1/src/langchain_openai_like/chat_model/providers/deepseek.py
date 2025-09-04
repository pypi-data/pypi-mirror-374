from typing import Any, Callable, Dict, Literal, Optional, Sequence, Union

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils import from_env, secret_from_env
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field, SecretStr

from .base_model import BaseChatOpenAILikeModel


class ChatDeepSeekModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="deepseek-chat")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("DEEPSEEK_API_KEY", default=None),
    )
    api_base: str = Field(
        default_factory=from_env(
            "DEEPSEEK_API_BASE",
            default="https://api.deepseek.com/v1",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-deepseek-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "DEEPSEEK_API_KEY"}

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

        if strict:
            self.api_base = self.api_base.replace("v1", "beta")

            formatted_tools = []
            for tool in tools:
                openai_tool = convert_to_openai_tool(tool, strict=strict)
                openai_tool["function"]["strict"] = True
                formatted_tools.append(openai_tool)

            tools = formatted_tools

        return super().bind_tools(
            tools,
            tool_choice=tool_choice,
            strict=strict,
            parallel_tool_calls=parallel_tool_calls,
            **kwargs,
        )
