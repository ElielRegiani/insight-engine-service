"""HTTP client for ML Service: POST /predict with retries."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import httpx

from app.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class MLServiceClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def predict(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.strip().upper()
        base = self.settings.ml_service_base_url.rstrip("/")
        url = f"{base}/predict"
        payload = {"symbol": sym}
        attempts = max(1, self.settings.ml_service_max_retries)
        last_err: Optional[Exception] = None
        for i in range(attempts):
            try:
                with httpx.Client(timeout=self.settings.ml_service_timeout_seconds) as client:
                    r = client.post(url, json=payload)
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                last_err = e
                logger.warning(
                    "ml_service_predict_failed",
                    extra={"symbol": sym, "attempt": i + 1, "error": str(e)},
                )
                if i < attempts - 1:
                    time.sleep(self.settings.ml_service_retry_backoff_seconds)
        raise RuntimeError(f"ML Service predict failed for {sym}") from last_err
