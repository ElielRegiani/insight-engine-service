from app.services.context_builder import (
    build_explanation_context,
    extract_symbol_from_question,
    normalize_snapshot,
)


def test_extract_symbol():
    assert extract_symbol_from_question("Comprar PETR4 agora?") == "PETR4"
    assert extract_symbol_from_question("sem ticker aqui") is None


def test_normalize_snapshot():
    n = normalize_snapshot({"symbol": "x", "price": 10.5, "rsi": 55.0})
    assert n["price"] == 10.5
    assert n["rsi"] == 55.0


def test_build_explanation_context():
    ctx = build_explanation_context(
        "PETR4",
        {"price": 30, "rsi": 60, "sma": 29, "volume": 1e6},
        {"prediction": "UP", "confidence": 0.8, "features_used": {"rsi": 60}},
    )
    assert ctx["prediction"] == "UP"
    assert ctx["confidence"] == 0.8
