"""Unit tests for app.threat_analysis.schemas.response."""

from app.threat_analysis.schemas import (
    AnalysisResponse,
    Component,
    RiskLevel,
    Threat,
)


class TestRiskLevel:
    def test_low(self):
        assert RiskLevel.from_score(0) == RiskLevel.LOW
        assert RiskLevel.from_score(2.5) == RiskLevel.LOW

    def test_medium(self):
        assert RiskLevel.from_score(3) == RiskLevel.MEDIUM
        assert RiskLevel.from_score(5) == RiskLevel.MEDIUM

    def test_high(self):
        assert RiskLevel.from_score(6) == RiskLevel.HIGH
        assert RiskLevel.from_score(7.5) == RiskLevel.HIGH

    def test_critical(self):
        assert RiskLevel.from_score(8) == RiskLevel.CRITICAL
        assert RiskLevel.from_score(10) == RiskLevel.CRITICAL


class TestAnalysisResponse:
    def test_threat_count(self):
        r = AnalysisResponse(
            model_used="test",
            components=[],
            connections=[],
            threats=[
                Threat(
                    component_id="a",
                    threat_type="Spoofing",
                    description="x",
                    mitigation="y",
                )
            ],
            risk_score=5.0,
            risk_level=RiskLevel.MEDIUM,
        )
        assert r.threat_count == 1

    def test_component_count(self):
        r = AnalysisResponse(
            model_used="test",
            components=[Component(id="c1", type="Server", name="Web")],
            connections=[],
            threats=[],
            risk_score=3.0,
            risk_level=RiskLevel.LOW,
        )
        assert r.component_count == 1
