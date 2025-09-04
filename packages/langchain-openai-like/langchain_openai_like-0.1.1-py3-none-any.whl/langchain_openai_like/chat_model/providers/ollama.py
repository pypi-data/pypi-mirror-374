from json import JSONDecodeError
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union, cast

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.utils import from_env, secret_from_env
import openai
from pydantic import Field, SecretStr

from .base_model import BaseChatOpenAILikeModel


class ChatOllamaModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("OLLAMA_API_KEY", default="sk-ollama"),
    )
    api_base: str = Field(
        default_factory=from_env(
            "OLLAMA_API_BASE",
            default="http://localhost:11434/v1",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-ollama-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "OLLAMA_API_KEY"}

    def _create_chat_result(
        self,
        response: Union[dict, openai.BaseModel],
        generation_info: Optional[Dict] = None,
    ) -> ChatResult:
        rtn = super()._create_chat_result(response, generation_info)

        if not isinstance(response, openai.BaseModel):
            return rtn

        content = response.choices[0].message.content  # type: ignore

        if "<think>" in content and "</think>" in content:
            reasoning_content = (
                content.split("<think>")[1].split("</think>")[0]  # type: ignore
            )
            if reasoning_content:
                if reasoning_content != "\n\n" and reasoning_content != "":
                    rtn.generations[0].message.additional_kwargs[
                        "reasoning_content"
                    ] = reasoning_content
                rtn.generations[0].message.content = rtn.generations[
                    0
                ].message.content.replace(f"<think>{reasoning_content}</think>", "")  # type: ignore
        return rtn

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        kwargs["stream_options"] = {"include_usage": True}
        think = False
        try:
            for chunk in super()._stream(
                messages,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            ):
                content = cast(str, chunk.message.content)
                if "<think>" in content or (think and "</think>" not in content):
                    think = True
                    reasoning_content = content.replace("<think>", "")
                    chunk.message.additional_kwargs["reasoning_content"] = (
                        reasoning_content
                    )
                    chunk.message.content = ""
                if "</think>" in content:
                    think = False
                    chunk.message.content = content.replace("</think>", "")
                    chunk.message.additional_kwargs["reasoning_content"] = (
                        chunk.message.content
                    )
                    chunk.message.content = ""

                yield chunk
        except JSONDecodeError as e:
            raise JSONDecodeError(
                f"Your {self.provider.upper()} API returned an invalid response. "
                "Please check the API status and try again.",
                e.doc,
                e.pos,
            ) from e

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        kwargs["stream_options"] = {"include_usage": True}
        think = False
        try:
            async for chunk in super()._astream(
                messages,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            ):
                content = cast(str, chunk.message.content)
                if "<think>" in content or (think and "</think>" not in content):
                    think = True
                    reasoning_content = content.replace("<think>", "")
                    chunk.message.additional_kwargs["reasoning_content"] = (
                        reasoning_content
                    )
                    chunk.message.content = ""
                if "</think>" in content:
                    think = False
                    chunk.message.content = content.replace("</think>", "")
                    chunk.message.additional_kwargs["reasoning_content"] = (
                        chunk.message.content
                    )
                    chunk.message.content = ""

                yield chunk
        except JSONDecodeError as e:
            raise JSONDecodeError(
                f"Your {self.provider.upper()} API  returned an invalid response. "
                "Please check the API status and try again.",
                e.doc,
                e.pos,
            ) from e
