"""完整 Tier1 安全审查解析测试（SkillSpector + SkillEvaluator Tier1）。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_recommend.security import (
    SPECTOR_JSON,
    TIER1_JSON,
    compute_security_verdict,
    load_security_from_report,
    parse_security_dir,
)


def _sp(score=0, severity="none", recommendation="safe", max_issue_severity="none",
        issues=None) -> dict:
    return {
        "risk_assessment": {
            "score": score,
            "severity": severity,
            "recommendation": recommendation,
            "max_issue_severity": max_issue_severity,
        },
        "issues": issues or [],
    }


def _t1(critical=0, high=0, medium=0, low=0, finding_groups=None) -> dict:
    return {
        "overall_status": "pass" if critical == 0 and high == 0 else "fail",
        "severity_counts": {
            "critical": critical, "high": high, "medium": medium, "low": low,
        },
        "finding_groups": finding_groups or [],
    }


def _sp_parsed(max_issue_severity="NONE", recommendation="SAFE") -> dict:
    return {
        "risk_score": 0,
        "severity": "NONE",
        "recommendation": recommendation,
        "max_issue_severity": max_issue_severity,
        "issue_count": 0,
    }


def _t1_parsed(critical=0, high=0) -> dict:
    return {
        "overall_status": "pass" if critical == 0 and high == 0 else "fail",
        "severity_counts": {"critical": critical, "high": high, "medium": 0, "low": 0},
    }


class TestComputeVerdict(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(compute_security_verdict(_sp_parsed(), _t1_parsed()), "safe")

    def test_safe_via_recommendation_even_with_medium(self):
        self.assertEqual(compute_security_verdict(_sp_parsed(max_issue_severity="MEDIUM"), _t1_parsed()), "safe")

    def test_unsafe_on_skillspector_high(self):
        # recommendation 非 SAFE 且 max_issue_severity=HIGH → unsafe
        sp = _sp_parsed(max_issue_severity="HIGH", recommendation="REVIEW")
        self.assertEqual(compute_security_verdict(sp, _t1_parsed()), "unsafe")

    def test_unsafe_on_tier1_high(self):
        self.assertEqual(compute_security_verdict(_sp_parsed(), _t1_parsed(high=1)), "unsafe")

    def test_missing_when_report_absent(self):
        self.assertEqual(compute_security_verdict({}, {}), "missing")
        self.assertEqual(compute_security_verdict(None, None), "missing")


class TestParseSecurityDir(unittest.TestCase):
    def test_parse_collects_findings(self):
        sp = _sp(severity="critical", max_issue_severity="critical",
                 issues=[{"severity": "critical", "message": "danger"}])
        t1 = _t1(high=1, finding_groups=[{"severity": "high", "message": "t1 danger"}])
        ev = parse_security_dir(sp, t1)
        self.assertEqual(ev.verdict, "unsafe")
        sources = {f["source"] for f in ev.high_severity_findings}
        self.assertEqual(sources, {"skillspector", "tier1"})
        self.assertEqual(ev.skillspector["issue_count"], 1)
        self.assertEqual(ev.tier1["severity_counts"]["high"], 1)

    def test_parse_collects_findings_from_real_fields(self):
        # 真实 SkillSpector 产物用 finding/explanation 而非 message/title
        sp = _sp(severity="high", recommendation="caution", max_issue_severity="high",
                 issues=[{"severity": "high", "finding": ".env ", "explanation": "credential access"}])
        t1 = _t1(high=0)
        ev = parse_security_dir(sp, t1)
        self.assertEqual(ev.verdict, "unsafe")
        self.assertEqual(ev.high_severity_findings[0]["message"], ".env")

    def test_parse_missing(self):
        ev = parse_security_dir(None, None)
        self.assertEqual(ev.verdict, "missing")


class TestLoadSecurityFromReport(unittest.TestCase):
    def _write_reports(self, root: Path, skill: str, sp: dict, t1: dict) -> Path:
        subdir = root / skill
        subdir.mkdir(parents=True)
        (subdir / SPECTOR_JSON).write_text(json.dumps(sp), encoding="utf-8")
        (subdir / TIER1_JSON).write_text(json.dumps(t1), encoding="utf-8")
        return subdir

    def test_load_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_reports(root, "calc-pro", _sp(), _t1())
            ev = load_security_from_report("calc-pro", root)
            self.assertIsNotNone(ev)
            self.assertEqual(ev.verdict, "safe")

    def test_load_none_when_dir_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_security_from_report("calc-pro", Path(tmp)))

    def test_load_none_when_skill_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_reports(Path(tmp), "other", _sp(), _t1())
            self.assertIsNone(load_security_from_report("calc-pro", Path(tmp)))

    def test_load_group_suffix(self):
        # 阶段零落盘方式 ``<组>_<skill>`` 应能被回退匹配到
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_reports(root, "G9_calculator", _sp(), _t1())
            ev = load_security_from_report("calculator", root)
            self.assertIsNotNone(ev)
            self.assertEqual(ev.verdict, "safe")


if __name__ == "__main__":
    unittest.main()
