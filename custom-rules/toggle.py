#!/usr/bin/env python3
"""规则开关（灰度控制）—— 按 select.yaml 组装 staging 目录。

设计定位（规则 A 与规则 B 分离）：
  规则 A = 白名单放行（抑制层 allow_domain），**不新增任何 finding**。
           它的唯一作用是放行「发往企业白名单域名的外发 finding」，
           由 --baseline /custom-rules/baseline.yaml 挂载，**不经过本脚本**。
  规则 B = 明文凭证检测（cvte_credential_inline.yar），**新增 finding**。
           由 --yara-rules-dir /custom-rules/staged 挂载，本脚本负责复制。

因此本脚本只处理规则 B 的检测规则文件；规则 A 的白名单开关见 select.yaml
的 `rule_a`（提示运行侧是否追加 --baseline），不落地任何 .yar。

用法：
    python3 custom-rules/toggle.py

之后用（以 A+B 为例）：
    docker compose run --rm skillspector scan /scan/security/custom-rules-range \
      --yara-rules-dir /custom-rules/staged --baseline /custom-rules/baseline.yaml \
      --no-llm --format json

仅依赖标准库（宿主机无 pyyaml），select.yaml 采用固定二维结构，用最小解析；
对未知 key 直接忽略，对非法值 fail-closed（报错退出）。
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

# rule key -> (源 .yar 文件名, 人类可读描述)
# 注意：规则 A（白名单）不在此表 —— 它不新增 finding，不挂检测规则。
RULE_FILES = {
    "rule_b": ("cvte_credential_inline.yar", "规则 B：禁止明文凭证内嵌命令行/连接串"),
}


def parse_select(path: Path) -> dict[str, bool]:
    """解析 select.yaml，取 `rules.rule_a/rule_b` 两键的 true/false。"""
    text = path.read_text(encoding="utf-8")
    if "rules:" not in text:
        raise SystemExit(f"[toggle] {path} 缺少 `rules:` 段落，无法解析开关")
    result: dict[str, bool] = {}
    for key in ("rule_a", "rule_b"):
        # 允许 `rule_a: true` / `rule_a: true # 注释` 两种形态
        m = re.search(rf"^\s*{re.escape(key)}\s*:\s*(true|false)\b", text, re.MULTILINE)
        if not m:
            raise SystemExit(f"[toggle] {path} 未找到开关 `{key}: true|false`")
        result[key] = m.group(1).lower() == "true"
    return result


def assemble(script_dir: Path, selection: dict[str, bool]) -> None:
    staged = script_dir / "staged"
    if staged.exists():
        shutil.rmtree(staged)
    staged.mkdir()

    # 规则 A（白名单）不落地文件，仅提示运行侧是否追加 --baseline
    rule_a = selection.get("rule_a", False)
    if rule_a:
        print("[toggle] 规则 A（白名单放行）已启用 → 运行时追加 --baseline /custom-rules/baseline.yaml（不新增 finding）")
    else:
        print("[toggle] 规则 A（白名单放行）未启用 → 不追加 --baseline（白名单域名的外发将按误报保留）")

    enabled_b = [key for key, on in selection.items() if on and key in RULE_FILES]
    if not enabled_b:
        print("[toggle] 规则 B 未启用 → staged/ 为空（不挂检测规则）")
        return

    for key in enabled_b:
        src_name, desc = RULE_FILES[key]
        src = script_dir / src_name
        if not src.is_file():
            raise SystemExit(f"[toggle] 源规则文件缺失：{src}")
        shutil.copy2(src, staged / src_name)
        print(f"[toggle] 启用 {desc} → 复制 {src_name} 到 staged/")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    select_path = script_dir / "select.yaml"
    if not select_path.is_file():
        raise SystemExit(f"[toggle] 找不到 {select_path}")
    selection = parse_select(select_path)
    assemble(script_dir, selection)
    staged = script_dir / "staged"
    files = sorted(p.name for p in staged.iterdir()) if staged.exists() else []
    print(f"[toggle] staged/ 当前内容：{files if files else '(空)'}")


if __name__ == "__main__":
    sys.exit(main())
