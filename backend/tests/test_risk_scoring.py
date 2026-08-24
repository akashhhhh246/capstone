import pytest
from app.ml.risk.risk_scoring_service import RiskScoringService

def test_explainable_risk_scoring_high():
    high_risk = RiskScoringService.calculate_risk_score(
        ai_probability=0.92,
        propagation_velocity=18.5,
        platform_count=4,
        branching_factor=3.5,
        derived_variant_count=4,
        gnn_score=0.85,
        bot_account_ratio=0.80
    )

    assert high_risk["risk_score"] >= 0.70
    assert high_risk["severity"] in ["HIGH", "CRITICAL"]
    assert len(high_risk["reasons"]) >= 3
    # Verify reasons explain key factors
    reasons_text = " ".join(high_risk["reasons"])
    assert "synthetic" in reasons_text.lower() or "velocity" in reasons_text.lower()

def test_explainable_risk_scoring_low():
    low_risk = RiskScoringService.calculate_risk_score(
        ai_probability=0.05,
        propagation_velocity=1.2,
        platform_count=1,
        branching_factor=1.1,
        derived_variant_count=0,
        gnn_score=0.10,
        bot_account_ratio=0.0
    )

    assert low_risk["risk_score"] < 0.40
    assert low_risk["severity"] == "LOW"
    assert len(low_risk["reasons"]) >= 1
