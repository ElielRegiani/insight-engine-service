from unittest.mock import MagicMock

from app.services.insight_service import InsightService


def test_explain_uses_clients():
    data = MagicMock()
    data.get_market_snapshot.return_value = {
        "symbol": "PETR4",
        "price": 32.0,
        "rsi": 50.0,
        "sma": 31.0,
        "volume": 1_000_000.0,
    }
    ml = MagicMock()
    ml.predict.return_value = {
        "symbol": "PETR4",
        "prediction": "UP",
        "confidence": 0.7,
        "features_used": {"rsi": 50, "sma": 31, "volume": 1e6},
    }
    llm = MagicMock()
    llm.complete.return_value = "Explicação sintética."

    svc = InsightService(data_client=data, ml_client=ml, llm=llm)
    out = svc.explain("PETR4")

    assert out["symbol"] == "PETR4"
    assert out["prediction"] == "UP"
    assert out["explanation"] == "Explicação sintética."
    data.get_market_snapshot.assert_called_once_with("PETR4")
    ml.predict.assert_called_once_with("PETR4")
    llm.complete.assert_called_once()


def test_ask_requires_symbol():
    svc = InsightService()
    svc.data = MagicMock()
    svc.ml = MagicMock()
    svc.llm = MagicMock()
    try:
        svc.ask("qual o melhor investimento?")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "symbol" in str(e).lower() or "ticker" in str(e).lower()
