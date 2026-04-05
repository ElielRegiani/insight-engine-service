"""Builds RAG context dicts from Data + ML payloads."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

TICKER_BR = re.compile(r"\b([A-Z]{4}\d)\b")


def extract_symbol_from_question(question: str) -> Optional[str]:
    m = TICKER_BR.search(question.upper())
    return m.group(1) if m else None


def _num(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def normalize_snapshot(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten snapshot for prompts (price, rsi, sma, volume)."""
    price = raw.get("price") or raw.get("close") or raw.get("last")
    return {
        "symbol": str(raw.get("symbol", "")).upper(),
        "price": _num(price),
        "rsi": _num(raw.get("rsi")),
        "sma": _num(raw.get("sma")),
        "volume": _num(raw.get("volume")),
        "timestamp": raw.get("timestamp"),
    }


def build_explanation_context(
    symbol: str,
    snapshot: Dict[str, Any],
    ml_result: Dict[str, Any],
) -> Dict[str, Any]:
    snap = normalize_snapshot(snapshot)
    feats = ml_result.get("features_used") or {}
    return {
        "symbol": symbol.upper(),
        "price": snap.get("price"),
        "rsi": snap.get("rsi"),
        "sma": snap.get("sma"),
        "volume": snap.get("volume"),
        "prediction": ml_result.get("prediction", "UNKNOWN"),
        "confidence": _num(ml_result.get("confidence")) or 0.0,
        "model_features_rsi": _num(feats.get("rsi")),
        "model_features_sma": _num(feats.get("sma")),
        "model_features_volume": _num(feats.get("volume")),
    }


def build_qa_context(
    symbol: str,
    snapshot: Dict[str, Any],
    ml_result: Optional[Dict[str, Any]],
) -> str:
    snap = normalize_snapshot(snapshot)
    lines = [
        f"Ativo: {symbol.upper()}",
        f"Preço atual: {snap.get('price')}",
        f"RSI: {snap.get('rsi')}",
        f"SMA: {snap.get('sma')}",
        f"Volume: {snap.get('volume')}",
    ]
    if ml_result:
        lines.extend(
            [
                "",
                "Previsão do modelo:",
                f"- Direção: {ml_result.get('prediction', 'UNKNOWN')}",
                f"- Confiança: {ml_result.get('confidence')}",
            ]
        )
    return "\n".join(lines)


def build_summary_context(rows_per_symbol: List[Dict[str, Any]]) -> str:
    blocks: List[str] = []
    for row in rows_per_symbol:
        sym = row.get("symbol", "")
        blocks.append(
            f"- {sym}: preço {row.get('price')}, RSI {row.get('rsi')}, "
            f"SMA {row.get('sma')}, volume {row.get('volume')}"
        )
    return "Dados recentes por ativo:\n" + "\n".join(blocks)
