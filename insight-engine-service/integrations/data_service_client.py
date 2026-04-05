"""HTTP client for Data Service: snapshot and history with retries."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import httpx

from app.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class DataServiceClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def _request(
        self,
        method: str,
        path: str,
    ) -> Dict[str, Any]:
        base = self.settings.data_service_base_url.rstrip("/")
        url = f"{base}{path}"
        attempts = max(1, self.settings.data_service_max_retries)
        last_err: Optional[Exception] = None
        for i in range(attempts):
            try:
                with httpx.Client(timeout=self.settings.data_service_timeout_seconds) as client:
                    r = client.request(method, url)
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                last_err = e
                logger.warning(
                    "data_service_request_failed",
                    extra={"url": url, "attempt": i + 1, "error": str(e)},
                )
                if i < attempts - 1:
                    time.sleep(self.settings.data_service_retry_backoff_seconds)
        raise RuntimeError(f"Data Service request failed: {url}") from last_err

    def get_market_snapshot(self, symbol: str) -> Dict[str, Any]:
        """Prefer GET /market-data/{symbol}; fallback to last row of /history."""
        sym = symbol.strip().upper()
        try:
            return self._request("GET", f"/market-data/{sym}")
        except Exception as e:
            logger.info(
                "market_snapshot_fallback_history",
                extra={"symbol": sym, "error": str(e)},
            )
        hist = self.get_market_history(sym)
        rows: List[Dict[str, Any]] = hist.get("data") or []
        if not rows:
            raise ValueError(f"No market data rows for {sym}")
        last = rows[-1]
        return {
            "symbol": sym,
            "price": last.get("price"),
            "rsi": last.get("rsi"),
            "sma": last.get("sma"),
            "volume": last.get("volume"),
            "timestamp": last.get("timestamp"),
        }

    def get_market_history(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.strip().upper()
        return self._request("GET", f"/market-data/{sym}/history")
