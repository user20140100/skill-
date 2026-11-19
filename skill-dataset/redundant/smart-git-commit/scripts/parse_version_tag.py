#!/usr/bin/env python3
"""Derive the BIOS version identifier from a git branch name.

Usage:
    python parse_version_tag.py "CCB-H340-MA01/CRB_R02.03-Pre/Customer/<client>/V0.04"
    git branch --show-current | python parse_version_tag.py

Config (client whitelist + non-client keywords) is read from ../customers.md.
The two regexes below are kept in code on purpose -- see customers.md section 4
for the rationale and the forced-false-positive list.

Output: one JSON object on stdout.
Exit code: 0 = high confidence (tag usable), 1 = low confidence (ask the user).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CONFIG_NAME = "customers.md"

BASELINE_RE = re.compile(r"^CRB[_：:]\d", re.IGNORECASE)
VERSION_RE = re.compile(
    r"^[VT]\d+(?:\.\d+)*[a-zA-Z]*(?:-[A-Za-z0-9_.]+)?$", re.IGNORECASE
)
SHORT_CODE_RE = re.compile(r"^[A-Z]{2,4}$")
PERSONAL_RE = re.compile(r"^[a-z]{2,5}$")

CUSTOMER_MARKERS = {"customer", "oem", "custom", "定制", "客户"}

STRIP_PREFIXES = ("origin/", "Branch_", "branch_")


def load_config(config_path: Path) -> tuple[dict[str, str], set[str]]:
    """Parse customers.md: markdown tables under '## 一' (whitelist) and '## 二' (keywords).

    Section 一 rows are `| segment[=display] | display | evidence |` -- only the first
    two cells are read, so the evidence column cannot leak into the whitelist.
    Section 二 rows are `| category | `kw1` `kw2` ... |` -- every cell after the first
    is read, so the category label never becomes a keyword.

    A whitelist cell may contain several `backticked` tokens; the form `segment=display`
    maps a branch segment to the name printed in the commit.
    """
    whitelist: dict[str, str] = {}
    keywords: set[str] = set()
    if not config_path.is_file():
        return whitelist, keywords

    section = ""
    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not any(cells):
            continue

        if section.startswith("一"):
            tokens = cells[:2]
            source = whitelist
        elif section.startswith("二"):
            tokens = cells[1:]
            source = keywords
        else:
            continue

        for cell in tokens:
            for token in re.findall(r"`([^`]+)`", cell):
                token = token.strip()
                if not token:
                    continue
                if source is whitelist:
                    seg, _, display = token.partition("=")
                    seg, display = seg.strip(), display.strip()
                    if seg:
                        whitelist[seg] = display or seg
                else:
                    keywords.add(token)
    return whitelist, keywords


def normalize(branch: str) -> list[str]:
    text = branch.strip()
    changed = True
    while changed:
        changed = False
        for prefix in STRIP_PREFIXES:
            if text.startswith(prefix):
                text = text[len(prefix) :]
                changed = True
    return [seg.strip() for seg in text.split("/") if seg.strip()]


def resolve(branch: str, whitelist: dict[str, str], keywords: set[str]) -> dict:
    segments = normalize(branch)
    result: dict = {
        "branch": branch,
        "segments": segments,
        "tag": None,
        "board": None,
        "client": None,
        "version": None,
        "confidence": "low",
        "reason": "",
    }
    if not segments:
        result["reason"] = "分支名为空或无法切段"
        return result

    # 1. version: last matching segment, segment case preserved
    version_index = None
    for i in range(len(segments) - 1, -1, -1):
        if VERSION_RE.match(segments[i]):
            version_index = i
            break

    # 2. trunk = everything before the version; the rest are personal/temp suffixes
    trunk = segments[:version_index] if version_index is not None else segments
    if not trunk:
        result["reason"] = "版本段之前没有板型段"
        return result

    # 3. board: first trunk segment, kept verbatim
    board = trunk[0]
    if not any(ch.isdigit() for ch in board):
        result["reason"] = f"板型段判定失败：第一段 '{board}' 不含数字，像是个人/组织前缀"
        return result
    result["board"] = board

    if version_index is None:
        result["reason"] = (
            f"版本段缺失：没有任何段匹配版本正则（V0.04 / T0.01 / T0.00-XMC），"
            f"板型已认到 '{board}' -> 必须问用户"
        )
        return result
    result["version"] = segments[version_index]

    # 4. client: candidates sit after the baseline segment
    rest = [seg for seg in trunk[1:] if not BASELINE_RE.match(seg)]
    for i, seg in enumerate(rest):
        if seg.lower() in CUSTOMER_MARKERS:
            nxt = rest[i + 1] if i + 1 < len(rest) else None
            if nxt and not is_keyword(nxt, keywords):
                result["client"] = whitelist.get(nxt, nxt)
                result["reason"] = f"规则 a：客户标记段 '{seg}' 的下一段 '{nxt}'"
                break
            result["reason"] = f"规则 a 失败：'{seg}' 后面没有可用的客户名"
            return result
    else:
        for seg in rest:
            if seg in whitelist:
                result["client"] = whitelist[seg]
                result["reason"] = f"规则 b：'{seg}' 命中客户白名单"
                break
        else:
            unknown = [
                seg
                for seg in rest
                if not is_keyword(seg, keywords) and SHORT_CODE_RE.match(seg)
            ]
            if unknown:
                result["reason"] = (
                    f"规则 c：'{unknown[0]}' 是未入白名单的全大写短码，"
                    "无法确定是否为客户 -> 必须问用户"
                )
            else:
                result["reason"] = (
                    "规则 d：余段只有阶段/类型/占位符/人名，判定为无客户线，"
                    "不能写「主板Bios定制」-> 必须问用户"
                )
            return result

    # 5. assemble
    result["confidence"] = "high"
    result["tag"] = f"{result['client']}{board}主板Bios定制{result['version']}"
    return result


def is_keyword(seg: str, keywords: set[str]) -> bool:
    if seg in keywords:
        return True
    if seg.lower() in {k.lower() for k in keywords}:
        return True
    return bool(PERSONAL_RE.match(seg))


def main() -> int:
    if len(sys.argv) > 1:
        branch = " ".join(sys.argv[1:])
    else:
        branch = sys.stdin.read().strip()
    if not branch:
        print(json.dumps({"error": "no branch name given"}, ensure_ascii=False))
        return 1

    whitelist, keywords = load_config(Path(__file__).resolve().parent.parent / CONFIG_NAME)
    result = resolve(branch, whitelist, keywords)
    result["whitelist_size"] = len(whitelist)
    result["keyword_size"] = len(keywords)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["confidence"] == "high" else 1


if __name__ == "__main__":
    sys.exit(main())
