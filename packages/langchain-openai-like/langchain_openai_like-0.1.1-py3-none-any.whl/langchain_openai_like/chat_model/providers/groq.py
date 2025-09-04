from typing import Any, Callable, Dict, Literal, Optional, Sequence, Type, Union


from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.utils import from_env, secret_from_env
from langchain_core.utils.function_calling import BaseTool
import openai
from pydantic import Field, SecretStr

from .base_model import BaseChatOpenAILikeModel


class ChatGroqModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("GROQ_API_KEY", default=None),
    )
    api_base: str = Field(
        default_factory=from_env(
            "GROQ_API_BASE",
            default="https://api.groq.com/openai/v1",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-groq-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "GROQ_API_KEY"}

    @property
    def _default_params(self) -> Dict[str, Any]:
        if self.extra_body is None:
            self.extra_body = {"reasoning_format": "parsed"}
        else:
            self.extra_body = {
                **self.extra_body,
                "reasoning_format": "parsed",
            }

        return super()._default_params

    def _create_chat_result(
        self,
        response: Union[dict, openai.BaseModel],
        generation_info: Optional[Dict] = None,
    ) -> ChatResult:
        rtn = super()._create_chat_result(response, generation_info)

        if not isinstance(response, openai.BaseModel):
            return rtn

        if hasattr(response.choices[0].message, "reasoning"):  # type:ignore
            rtn.generations[0].message.additional_kwargs["reasoning_content"] = (
                response.choices[0].message.reasoning_content  # type:ignore
            )
        return rtn

    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict,
        default_chunk_class: Type,
        base_generation_info: Optional[Dict],
    ) -> Optional[ChatGenerationChunk]:
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk,
            default_chunk_class,
            base_generation_info,
        )
        if (choices := chunk.get("choices")) and generation_chunk:
            top = choices[0]
            if isinstance(generation_chunk.message, AIMessageChunk):
                if reasoning_content := top.get("delta", {}).get("reasoning"):
                    generation_chunk.message.additional_kwargs["reasoning_content"] = (
                        reasoning_content
                    )

        return generation_chunk

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
