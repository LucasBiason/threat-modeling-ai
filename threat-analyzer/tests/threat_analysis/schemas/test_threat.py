"""Unit tests for app.threat_analysis.schemas.threat."""

from app.threat_analysis.schemas import DreadScore, Threat


class TestDreadScore:
    def test_average(self):
        ds = DreadScore(
            damage=2,
            reproducibility=4,
            exploitability=6,
            affected_users=8,
            discoverability=10,
        )
        assert ds.average == 6.0


class TestThreat:
    def test_rounds_dread_score(self):
        t = Threat(
            component_id="c1",
            threat_type="Spoofing",
            description="d",
            mitigation="m",
            dread_score=5.678,
        )
        assert t.dread_score == 5.68

    def test_none_dread_score(self):
        t = Threat(
            component_id="c1",
            threat_type="Spoofing",
            description="d",
            mitigation="m",
            dread_score=None,
        )
        assert t.dread_score is None
