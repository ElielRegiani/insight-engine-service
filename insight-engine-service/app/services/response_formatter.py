"""Normalize LLM text for API responses."""

from __future__ import annotations

import re


def strip_mock_prefix(text: str) -> str:
    return re.sub(r"^\[MOCK LLM[^\]]*\]\s*", "", text, flags=re.DOTALL).strip() or text


def explanation_body(text: str) -> str:
    return strip_mock_prefix(text).strip()


def answer_body(text: str) -> str:
    return strip_mock_prefix(text).strip()


def summary_body(text: str) -> str:
    return strip_mock_prefix(text).strip()
