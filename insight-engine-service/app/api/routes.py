"""FastAPI routes for insight endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.insight_schema import (
    AskRequest,
    AskResponse,
    ExplainRequest,
    ExplainResponse,
    HealthResponse,
    SummaryRequest,
    SummaryResponse,
)
from app.services.insight_service import InsightService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["insight"])

_svc: InsightService | None = None


def get_service() -> InsightService:
    global _svc
    if _svc is None:
        _svc = InsightService()
    return _svc


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/insight/explain", response_model=ExplainResponse)
def explain(body: ExplainRequest) -> ExplainResponse:
    try:
        out = get_service().explain(body.symbol)
        return ExplainResponse(**out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("explain_failed")
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}") from e


@router.post("/insight/summary", response_model=SummaryResponse)
def summary(body: SummaryRequest) -> SummaryResponse:
    # Normalize legacy alias
    _ = body.type  # daily | daily_summary
    try:
        out = get_service().summarize_daily()
        return SummaryResponse(**out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("summary_failed")
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}") from e


@router.post("/insight/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    try:
        out = get_service().ask(body.question, body.symbol)
        return AskResponse(**out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("ask_failed")
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}") from e
