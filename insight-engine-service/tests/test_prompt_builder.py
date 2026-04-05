from pathlib import Path

from app.config.settings import Settings
from app.services.prompt_builder import PromptBuilder


def test_explanation_template_format(tmp_path: Path):
    td = tmp_path / "templates"
    td.mkdir(parents=True)
    (td / "explanation.txt").write_text(
        "P:{price} R:{rsi} {prediction}", encoding="utf-8"
    )
    (td / "qa.txt").write_text("Q:{question} C:{context}", encoding="utf-8")
    (td / "summary.txt").write_text("S:{market_data}", encoding="utf-8")

    s = Settings(templates_dir=td)
    pb = PromptBuilder(s)
    text = pb.explanation(
        {
            "symbol": "PETR4",
            "price": 1,
            "rsi": 2,
            "sma": 3,
            "volume": 4,
            "prediction": "UP",
            "confidence": 0.5,
        }
    )
    assert "P:1" in text and "UP" in text
