"""Load templates and substitute variables."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from app.config.settings import Settings, get_settings


class PromptBuilder:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _read(self, name: str) -> str:
        path: Path = self.settings.templates_dir / name
        return path.read_text(encoding="utf-8")

    def explanation(self, ctx: Dict[str, Any]) -> str:
        tpl = self._read("explanation.txt")
        return tpl.format(
            price=ctx.get("price", "n/d"),
            rsi=ctx.get("rsi", "n/d"),
            sma=ctx.get("sma", "n/d"),
            volume=ctx.get("volume", "n/d"),
            prediction=ctx.get("prediction", "n/d"),
            confidence=ctx.get("confidence", "n/d"),
            symbol=ctx.get("symbol", ""),
        )

    def qa(self, context: str, question: str) -> str:
        tpl = self._read("qa.txt")
        return tpl.format(context=context, question=question)

    def summary(self, market_block: str) -> str:
        tpl = self._read("summary.txt")
        return tpl.format(market_data=market_block)
