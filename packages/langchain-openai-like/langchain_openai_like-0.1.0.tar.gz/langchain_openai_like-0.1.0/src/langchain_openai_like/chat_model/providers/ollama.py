from typing import Dict, Optional

from langchain_core.utils import from_env, secret_from_env
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
            default="http://localhost:11434",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-ollama-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "OLLAMA_API_KEY"}
