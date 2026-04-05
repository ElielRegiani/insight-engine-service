"""Insight Service — FastAPI entrypoint."""

from __future__ import annotations

import logging
import sys

from fastapi import FastAPI
from pythonjsonlogger import jsonlogger

from app.api.routes import router
from app.config.settings import get_settings


def _configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    fmt = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


_configure_logging()

app = FastAPI(
    title="Insight Service",
    version="1.0.0",
    description="LLM + RAG: explicações, resumos e Q&A sobre ativos.",
)
app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"service": "insight-service", "docs": "/docs"}
