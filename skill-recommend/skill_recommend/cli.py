"""命令行入口：judge / pipeline / search 三个子命令。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .batch import (
    build_batch_report,
    build_batch_scan_commands,
    discover_skills,
    render_html as render_audit_html,
    render_markdown as render_audit_markdown,
)
from .config import SIMILAR_THRESHOLD, project_root
from .detect import detect_similar
from .judge import judge_from_inputs
from .llm import generate_narrative
from .models import RecommendationReport
from .pipeline import run_pipeline
from .report import render_markdown
from .search import merge_candidates, search_skills, semantic_candidates_from_report, skill_info


def _write_outputs(report: RecommendationReport, out: str | None) -> None:
    if out is None:
        print(report.report_markdown)
        return
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md_path = out_path if out_path.suffix else out_path.with_suffix(".md")
    json_path = md_path.with_suffix(".json")
    md_path.write_text(report.report_markdown, encoding="utf-8")
    json_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"报告已写入：{md_path}")
    print(f"JSON 已写入：{json_path}")


def _cmd_judge(args: argparse.Namespace) -> int:
    report = judge_from_inputs(
        args.similarity_report,
        args.results_dir,
        args.skills[0],
        args.skills[1],
        agent=args.agent,
        security_dir=args.security_dir,
    )

    semantic = semantic_candidates_from_report(args.company_report) if args.company_report else []
    keyword = search_skills(args.search) if args.search else []
    if semantic or keyword:
        report.external_candidates = merge_candidates(keyword, semantic)

    if args.llm:
        narrative = generate_narrative(report)
        if narrative:
            report.recommendation = narrative
        else:
            print("[warn] LLM 叙述生成失败，回退到模板叙述", file=sys.stderr)

    # 最终统一重新渲染，确保 external_candidates 与（可能的）LLM 叙述都反映到报告里。
    report.report_markdown = render_markdown(report)

    _write_outputs(report, args.out)
    return 0


def _cmd_detect(args: argparse.Namespace) -> int:
    result = detect_similar(
        args.base,
        library_rel=args.library,
        threshold=args.threshold,
        run=args.run,
    )
    if args.run and not result.get("executed"):
        print("[error] 相似检测执行失败：", result.get("failed_command"), file=sys.stderr)
        return 1
    if args.run:
        matches = result.get("matches", [])
        if not matches:
            print(f"[info] 未发现相似度 >= {args.threshold} 的公司 skill")
        else:
            print(f"相似公司 skill 列表（相似度 >= {args.threshold}）：")
            for m in matches:
                full_rel = f"{args.library}/{m.catalog_path}" if m.catalog_path else m.catalog_skill
                print(f"  {m.catalog_skill}\t{m.similarity:.3f}\t{m.classification}\t{full_rel}")
    return 0


def _cmd_pipeline(args: argparse.Namespace) -> int:
    result = run_pipeline(
        args.base,
        args.candidate,
        library_rel=args.library,
        eval_source=args.eval_source,
        agent=args.agent,
        model=args.model,
        run=args.run,
    )
    if args.run and not result.get("executed"):
        print("[error] 编排执行失败：", result.get("failed_command"), file=sys.stderr)
        return 1
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    if args.info:
        info = skill_info(args.info)
        print(info or f"[error] 未找到 skill：{args.info}")
        return 0 if info else 1
    candidates = search_skills(args.keyword)
    if not candidates:
        print(f"[warn] 未搜索到匹配 '{args.keyword}' 的 skill（或 cskills 不可用）")
        return 0
    for c in candidates:
        print(f"{c.name}\t{c.description}")
    return 0


def _resolve_host_path(value: str | None, root: Path) -> Path | None:
    """把 CLI 传入的宿主机路径解析为绝对路径（相对路径以仓库根为基准）。"""
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else root / p


def _write_audit_outputs(md: str, html: str, out: str | None, root: Path) -> None:
    if out is None:
        print(md)
        html_path = root / "reports" / "audit.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        print(f"[info] HTML 已写入：{html_path}")
        return
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = root / out_path
    md_path = out_path.with_suffix(".md")
    html_path = out_path.with_suffix(".html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    print(f"[info] Markdown 已写入：{md_path}")
    print(f"[info] HTML 已写入：{html_path}")


def _cmd_scan(args: argparse.Namespace) -> int:
    root = project_root()
    dataset_root = root / "skill-dataset"

    dir_arg = Path(args.dir)
    directory = dir_arg if dir_arg.is_absolute() else dataset_root / dir_arg
    if not directory.is_dir():
        print(f"[error] 目录不存在：{directory}", file=sys.stderr)
        return 1

    try:
        directory.relative_to(dataset_root)
        base = dataset_root
    except ValueError:
        base = directory
    skills = discover_skills(directory, base=base)
    if not skills:
        print(f"[info] 目录下未发现含 SKILL.md 的 skill：{directory}")
        return 0

    commands = build_batch_scan_commands(skills, use_llm=args.llm)
    if args.run:
        for cmd in commands:
            print(" ".join(cmd))
            rc = subprocess.run(cmd).returncode
            if rc != 0:
                print(f"[error] 命令执行失败（exit {rc}）：{' '.join(cmd)}", file=sys.stderr)
                return 1
    else:
        print(f"[dry-run] 发现 {len(skills)} 个 skill，将执行以下扫描命令（加 --run 真执行）：")
        for cmd in commands:
            print("  " + " ".join(cmd))

    report = build_batch_report(
        skills,
        security_dir=_resolve_host_path(args.security_dir, root),
        results_dir=_resolve_host_path(args.results_dir, root),
        agent=args.agent,
        manifest_path=_resolve_host_path(args.manifest, root),
        directory=args.dir,
    )
    _write_audit_outputs(
        render_audit_markdown(report),
        render_audit_html(report),
        args.out,
        root,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-recommend",
        description="冗余冲突 Skill 评估与更优 Skill 推荐",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_judge = sub.add_parser("judge", help="判定模式：输入已有 Tier2/Tier3 产物，输出推荐报告")
    p_judge.add_argument("--similarity-report", required=True, help="Tier2 similarity JSON 报告路径")
    p_judge.add_argument("--results-dir", required=True, help="Tier3 结果根目录（含各 skill 子目录）")
    p_judge.add_argument("--skills", nargs=2, required=True, metavar=("A", "B"), help="要比较的两个 skill 名")
    p_judge.add_argument("--agent", default=None, help="agent 名（默认取 result.json 第一个）")
    p_judge.add_argument("--security-dir", default=None, help="完整 Tier1 安全报告目录（含各 skill 的 skillspector.json / skillevaluator-tier1.json）")
    p_judge.add_argument("--search", default=None, help="联网搜索关键词（公司库 cskills）")
    p_judge.add_argument("--company-report", default=None, help="公司库语义匹配的 similarity 报告路径")
    p_judge.add_argument("--llm", action="store_true", help="用 LLM 增强推荐叙述（失败回退模板）")
    p_judge.add_argument("--out", default=None, help="输出文件路径（默认仅打印到 stdout）")
    p_judge.set_defaults(func=_cmd_judge)

    p_detect = sub.add_parser("detect", help="相似检测：正向 skill 对公司库 catalog 比对，列出相似公司 skill")
    p_detect.add_argument("--base", required=True, help="正向 skill 相对 skill-dataset 的路径")
    p_detect.add_argument("--library", default="library-20261118", help="公司库快照相对 skill-dataset 路径")
    p_detect.add_argument("--threshold", type=float, default=SIMILAR_THRESHOLD, help="相似度下限")
    p_detect.add_argument("--run", action="store_true", help="真正执行（默认 dry-run 只打印命令）")
    p_detect.set_defaults(func=_cmd_detect)

    p_pipe = sub.add_parser("pipeline", help="编排模式：生成/执行公司库比对 + 共享用例 Tier3 命令")
    p_pipe.add_argument("--base", required=True, help="正向 skill 相对 skill-dataset 的路径")
    p_pipe.add_argument("--candidate", required=True, help="选定的公司库 skill 相对 skill-dataset 的路径")
    p_pipe.add_argument("--library", default="library-20261118", help="公司库快照相对 skill-dataset 路径")
    p_pipe.add_argument("--eval-source", default=None, help="共享用例来源 skill 相对 skill-dataset 路径（可选，提供则复制其 evals 到双方）")
    p_pipe.add_argument("--agent", default="opencode")
    p_pipe.add_argument("--model", default="qwen3.8-flash")
    p_pipe.add_argument("--run", action="store_true", help="真正执行（默认 dry-run 只打印命令）")
    p_pipe.set_defaults(func=_cmd_pipeline)

    p_search = sub.add_parser("search", help="联网搜索公司库相关 skill")
    p_search.add_argument("--keyword", default=None, help="搜索关键词")
    p_search.add_argument("--info", default=None, help="查看某个 skill 详情")
    p_search.set_defaults(func=_cmd_search)

    p_scan = sub.add_parser("scan", help="批量扫描目录下所有 Skill，输出安全评级 + 沙盒对比的 Markdown/HTML 审计报告")
    p_scan.add_argument("--dir", required=True, help="扫描目录（相对 skill-dataset 的路径，如 library-demo）")
    p_scan.add_argument("--run", action="store_true", help="真正执行扫描命令（默认 dry-run 只打印）")
    p_scan.add_argument("--llm", action="store_true", help="启用 LLM 语义分析（默认 --no-llm 静态扫描；需网关凭据）")
    p_scan.add_argument("--security-dir", default="reports/security", help="Tier1 安全报告目录（宿主路径，相对仓库根）")
    p_scan.add_argument("--results-dir", default="reports/reco-results", help="Tier3 结果目录（宿主路径，相对仓库根）")
    p_scan.add_argument("--agent", default="opencode", help="Tier3 agent 名（默认 opencode）")
    p_scan.add_argument("--manifest", default="skill-dataset/manifest.json", help="标签清单路径（用于分类）")
    p_scan.add_argument("--out", default=None, help="报告输出路径（写 <out>.md 与 <out>.html；缺省打印 MD 到 stdout、HTML 写 reports/audit.html）")
    p_scan.set_defaults(func=_cmd_scan)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
