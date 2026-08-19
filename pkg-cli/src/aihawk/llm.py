"""OpenRouter (OpenAI-compatible) client config. Key from arg or env only."""
from __future__ import annotations

from typing import Mapping

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "z-ai/glm-4.6"


def resolve_key(explicit: str | None, env: Mapping[str, str]) -> str:
    key = explicit or env.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(
            "no OpenRouter key: pass --openrouter-key or set OPENROUTER_API_KEY"
        )
    return key


def resolve_model(explicit: str | None, env: Mapping[str, str]) -> str:
    return explicit or env.get("AIHAWK_MODEL") or DEFAULT_MODEL


def make_client(key: str):
    from openai import OpenAI
    return OpenAI(base_url=BASE_URL, api_key=key)
