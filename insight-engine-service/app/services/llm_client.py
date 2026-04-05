"""OpenAI-compatible chat completion; mock mode without API key."""

from __future__ import annotations

import logging
import time
from typing import Optional

import httpx

from app.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def complete(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        t0 = time.perf_counter()
        key = (self.settings.openai_api_key or "").strip()
        if not key:
            text = self._mock_response(user_prompt)
            logger.info(
                "llm_mock_response",
                extra={"latency_ms": round((time.perf_counter() - t0) * 1000, 2)},
            )
            return text

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        url = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.settings.openai_model,
            "messages": messages,
            "max_tokens": self.settings.llm_max_tokens,
            "temperature": self.settings.llm_temperature,
        }
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()

        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        content = (msg.get("content") or "").strip()
        latency_ms = (time.perf_counter() - t0) * 1000
        usage = data.get("usage") or {}
        logger.info(
            "llm_complete",
            extra={
                "latency_ms": round(latency_ms, 2),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
            },
        )
        return content or "Resposta vazia do modelo."

    def _mock_response(self, user_prompt: str) -> str:
        return (
            "[MOCK LLM — defina OPENAI_API_KEY] "
            "Resumo baseado no contexto injetado:\n\n"
            f"{user_prompt[:1200]}"
        )
