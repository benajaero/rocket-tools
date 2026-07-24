"""Tests for standards & reliability tools (design review, FMEA, catalog)."""

import pytest

from rocket_tools.standards import design_review_report, fmea_report, list_standards


class TestDesignReview:
    def test_governing_margin_is_minimum(self):
        r = design_review_report(
            [
                {"name": "spar", "margin_of_safety": 0.45},
                {"name": "rib", "margin_of_safety": 0.05},
                {"name": "skin", "margin_of_safety": 0.30},
            ]
        )
        assert r["summary"]["min_margin"] == 0.05
        assert r["summary"]["governing_item"] == "rib"
        assert r["verdict"] == "PASS"

    def test_negative_margin_fails(self):
        r = design_review_report(
            [
                {"name": "spar", "margin_of_safety": 0.45},
                {"name": "bracket", "margin_of_safety": -0.1},
            ]
        )
        assert r["verdict"] == "FAIL"
        assert r["summary"]["num_failing"] == 1

    def test_computes_margin_from_stress_pair(self):
        # MS = allowable/(FoS*actual) - 1 = 276/(1.5*150) - 1 = 0.2267
        r = design_review_report(
            [{"name": "panel", "allowable_stress_pa": 276e6, "actual_stress_pa": 150e6}]
        )
        assert r["items"][0]["margin_of_safety"] == pytest.approx(0.2267, abs=1e-3)

    def test_min_acceptable_margin_threshold(self):
        r = design_review_report(
            [{"name": "a", "margin_of_safety": 0.1}], min_acceptable_margin=0.25
        )
        assert r["verdict"] == "FAIL"  # 0.1 < 0.25

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            design_review_report([])

    def test_missing_data_raises(self):
        with pytest.raises(ValueError):
            design_review_report([{"name": "x"}])


class TestFMEA:
    def test_rpn_and_ranking(self):
        r = fmea_report(
            [
                {"failure_mode": "low", "severity": 2, "occurrence": 2, "detection": 2},  # 8
                {"failure_mode": "high", "severity": 8, "occurrence": 5, "detection": 5},  # 200
                {"failure_mode": "mid", "severity": 4, "occurrence": 3, "detection": 3},  # 36
            ]
        )
        assert r["max_rpn"] == 200
        # ranked descending by RPN
        assert [i["failure_mode"] for i in r["items_ranked"]] == ["high", "mid", "low"]
        assert r["items_ranked"][0]["rpn"] == 200

    def test_high_priority_by_threshold(self):
        r = fmea_report(
            [{"failure_mode": "m", "severity": 5, "occurrence": 5, "detection": 5}],  # 125
            rpn_threshold=100,
        )
        assert r["num_high_priority"] == 1

    def test_high_priority_by_severity(self):
        # RPN below threshold but severity 9 => still high priority
        r = fmea_report(
            [{"failure_mode": "catastrophic", "severity": 9, "occurrence": 1, "detection": 1}],
            rpn_threshold=100,
        )
        assert r["items_ranked"][0]["high_priority"] is True

    def test_out_of_range_score_raises(self):
        with pytest.raises(ValueError):
            fmea_report([{"failure_mode": "x", "severity": 11, "occurrence": 1, "detection": 1}])


class TestCatalog:
    def test_lists_known_standards(self):
        cat = list_standards()
        ids = {s["id"] for s in cat["standards"]}
        assert "MIL-STD-1629A" in ids
        assert "NASA-STD-5001" in ids
        assert cat["count"] == len(cat["standards"])
