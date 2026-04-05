from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    symbol: str = Field(..., min_length=1, description="Ticker, e.g. PETR4")


class ExplainResponse(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    explanation: str


class SummaryRequest(BaseModel):
    type: Literal["daily", "daily_summary"] = Field(
        default="daily",
        description="Summary kind; daily_summary is accepted as alias for daily.",
    )


class SummaryResponse(BaseModel):
    summary: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    symbol: Optional[str] = Field(
        default=None,
        description="Optional ticker; if omitted, service tries to infer from the question.",
    )


class AskResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str
    service: str = "insight-service"
