#!/usr/bin/env python3
"""Summarize static Tier 1 JSON reports for selected company-library groups."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/yangyuhan/ai-agent-agent-skills")
BASE = ROOT / "reports/company-library-20261118/tier1"
STATUS = ROOT / "reports/company-library-20261118/tier1-status.txt"
OUT = ROOT / "reports/company-library-20261118/tier1-汇总.md"

SECURITY = ["Security Scan", "Code Risk Analysis", "Secrets Detection", "Code Integrity & Hygiene"]


def load_status() -> dict[tuple[str, str], int]:
    status = {}
    if STATUS.exists():
        for line in STATUS.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                status[(parts[1], parts[2])] = int(parts[0])
    return status


def summarize(path: pathlib.Path) -> dict:
    j = json.loads(path.read_text())
    results = {r["validator"]: r for r in j.get("results", [])}
    quality = (j.get("quality_summary") or [{}])[0]
    sec_fail = [v for v in SECURITY if results.get(v, {}).get("status") == "failed"]
    sec_high = sum(
        (results.get(v, {}).get("summary") or {}).get("critical_count", 0)
        + (results.get(v, {}).get("summary") or {}).get("high_count", 0)
        for v in SECURITY
    )
    pii = results.get("PII Scan", {})
    dep = results.get("Dependency Vulnerability Audit", {})
    return {
        "status": j.get("overall_status"),
        "passed": j.get("overall_passed"),
        "severity": j.get("severity_counts", {}),
        "quality_score": quality.get("overall_score"),
        "quality_grade": quality.get("grade"),
        "sec_fail": sec_fail,
        "sec_high": sec_high,
        "pii_status": pii.get("status"),
        "dep_status": dep.get("status"),
        "missing": not path.exists(),
    }


def findings_text(path: pathlib.Path) -> str:
    j = json.loads(path.read_text())
    out = []
    for r in j.get("results", []):
        if r["validator"] not in SECURITY + ["PII Scan"]:
            continue
        for f in r.get("findings", []):
            if f.get("severity") in {"critical", "high"}:
                out.append(f"[{f['severity']}] {r['validator']}: {f['message'][:120]}")
    return "; ".join(out[:4])


def main() -> None:
    status = load_status()
    groups = {}
    for gid in ["G2", "G4", "G9"]:
        for d in sorted((BASE / gid).iterdir()):
            if not d.is_dir():
                continue
            p = d / "skillevaluator-tier1.json"
            if not p.exists():
                groups.setdefault(gid, []).append(
                    {"name": d.name, "missing": True, "status": "MISSING", "passed": None}
                )
                continue
            row = summarize(p)
            row["name"] = d.name
            row["findings"] = findings_text(p)
            row["rc"] = status.get((gid, d.name))
            groups.setdefault(gid, []).append(row)

    lines = ["# 公司 Skill 库 Tier1 静态扫描汇总（--no-llm）", ""]
    lines.append("- 对象：G2 代码审查 / G4 需求 PRD / G9 日志诊断，共 37 个 skill")
    lines.append("- 命令：`skillevaluator tier1 <path> --no-llm`（静态；LLM 语义安全扫描未开启）")
    lines.append("- 说明：`安全` 只统计 Security/Code Risk/Secrets/Code Integrity 四类；PII 单独列出。")
    lines.append("")
    for gid in ["G2", "G4", "G9"]:
        rows = groups.get(gid, [])
        ok = sum(1 for r in rows if r.get("passed"))
        sec_ok = sum(1 for r in rows if not r.get("sec_fail") and not r.get("missing"))
        lines.append(f"## {gid}（{len(rows)} 个）")
        lines.append("")
        lines.append(f"- 总体通过：{ok}/{len(rows)}；安全类通过：{sec_ok}/{len(rows)}")
        lines.append("")
        lines.append("| Skill | 总体 | 安全 | PII | 依赖 | 质量分 | C/H/M/L | 关键 finding |")
        lines.append("|---|---|---|---|---|---:|---|---|")
        for r in rows:
            if r.get("missing"):
                lines.append(f"| `{r['name']}` | MISSING | - | - | - | - | - | - |")
                continue
            sev = r.get("severity", {})
            lines.append(
                f"| `{r['name']}` | {r.get('status')} | "
                f"{'FAIL' if r.get('sec_fail') else 'pass'} | {r.get('pii_status')} | "
                f"{r.get('dep_status')} | {r.get('quality_score')} ({r.get('quality_grade')}) | "
                f"{sev.get('critical', 0)}/{sev.get('high', 0)}/{sev.get('medium', 0)}/{sev.get('low', 0)} | "
                f"{r.get('findings', '')} |"
            )
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
