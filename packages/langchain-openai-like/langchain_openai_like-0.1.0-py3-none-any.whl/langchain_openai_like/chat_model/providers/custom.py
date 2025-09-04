from typing import Dict, Optional

from langchain_core.utils import from_env, secret_from_env

from .base_model import BaseChatOpenAILikeModel
from pydantic import Field, SecretStr


class ChatOpenAILIkeModel(BaseChatOpenAILikeModel):
    model_name: str = Field(alias="model", default="")

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("OPENAI_LIKE_API_KEY", default=None),
    )
    api_base: str = Field(
        default_factory=from_env(
            "OPENAI_LIKE_API_BASE",
            default="",
        ),
    )

    @property
    def _llm_type(self) -> str:
        return "chat-openai-like-model"

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "OPENAILIKE_API_KEY"}
