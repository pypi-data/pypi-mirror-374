from typing import Dict, Optional


from langchain_core.utils import from_env, secret_from_env
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
