"""Orchestrates Data + ML + prompt + LLM + formatting."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional, Tuple

from app.config.settings import Settings, get_settings
from app.services.context_builder import (
    build_explanation_context,
    build_qa_context,
    build_summary_context,
    extract_symbol_from_question,
    normalize_snapshot,
)
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.services.response_formatter import answer_body, explanation_body, summary_body
from integrations.data_service_client import DataServiceClient
from integrations.ml_service_client import MLServiceClient

logger = logging.getLogger(__name__)


class InsightService:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        data_client: Optional[DataServiceClient] = None,
        ml_client: Optional[MLServiceClient] = None,
        prompts: Optional[PromptBuilder] = None,
        llm: Optional[LLMClient] = None,
    ):
        self.settings = settings or get_settings()
        self.data = data_client or DataServiceClient(self.settings)
        self.ml = ml_client or MLServiceClient(self.settings)
        self.prompts = prompts or PromptBuilder(self.settings)
        self.llm = llm or LLMClient(self.settings)
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if not entry:
            return None
        ts, payload = entry
        if time.time() - ts > self.settings.cache_ttl_seconds:
            return None
        return payload

    def _cache_set(self, key: str, payload: Dict[str, Any]) -> None:
        self._cache[key] = (time.time(), payload)

    def _safe_predict(self, symbol: str) -> Dict[str, Any]:
        try:
            return self.ml.predict(symbol)
        except Exception as e:
            logger.warning("ml_predict_fallback", extra={"symbol": symbol, "error": str(e)})
            return {
                "symbol": symbol.upper(),
                "prediction": "UNKNOWN",
                "confidence": 0.0,
                "features_used": {},
            }

    def explain(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.strip().upper()
        cache_key = f"explain:{sym}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        snap = self.data.get_market_snapshot(sym)
        ml_result = self._safe_predict(sym)
        ctx = build_explanation_context(sym, snap, ml_result)
        user_prompt = self.prompts.explanation(ctx)
        raw = self.llm.complete(user_prompt)
        explanation = explanation_body(raw)

        out = {
            "symbol": sym,
            "prediction": ml_result.get("prediction", "UNKNOWN"),
            "confidence": float(ml_result.get("confidence") or 0.0),
            "explanation": explanation,
        }
        self._cache_set(cache_key, out)
        return out

    def summarize_daily(self) -> Dict[str, str]:
        cache_key = "summary:daily"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return {"summary": cached["summary"]}

        rows: list[Dict[str, Any]] = []
        for sym in self.settings.summary_symbol_list:
            try:
                snap = self.data.get_market_snapshot(sym)
                n = normalize_snapshot(snap)
                n["symbol"] = sym
                rows.append(n)
            except Exception as e:
                logger.warning("summary_skip_symbol", extra={"symbol": sym, "error": str(e)})

        if not rows:
            raise ValueError("No market data available for summary symbols.")

        block = build_summary_context(rows)
        user_prompt = self.prompts.summary(block)
        raw = self.llm.complete(user_prompt)
        text = summary_body(raw)
        self._cache_set(cache_key, {"summary": text})
        return {"summary": text}

    def ask(self, question: str, symbol: Optional[str] = None) -> Dict[str, str]:
        sym = (symbol or "").strip().upper() or None
        if not sym:
            sym = extract_symbol_from_question(question)
        if not sym:
            raise ValueError(
                "Não foi possível identificar o ticker. Informe o campo 'symbol' ou cite o ativo "
                "(ex.: PETR4) na pergunta."
            )

        snap = self.data.get_market_snapshot(sym)
        ml_result = self._safe_predict(sym)
        ctx_text = build_qa_context(sym, snap, ml_result)
        user_prompt = self.prompts.qa(ctx_text, question)
        raw = self.llm.complete(
            user_prompt,
            system_prompt=(
                "Você é um assistente financeiro. Use apenas o contexto numérico fornecido. "
                "Se faltar dado, diga claramente. Não invente preços ou indicadores."
            ),
        )
        return {"answer": answer_body(raw)}
