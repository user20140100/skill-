"""编排模式：生成（并可选执行）skillevaluator 命令。

命令通过 ``docker compose run --rm skillevaluator`` 在容器内执行，路径映射
对齐 ``docker-compose.yml``：宿主机 ``./skill-dataset`` → 容器 ``/skills``，
宿主机 ``./reports`` → 容器 ``/app/reports``。

本模块只负责命令编排；产物解析与判定由 :mod:`skill_recommend.judge` 完成。
默认 dry-run（只打印命令），``run=True`` 才真正执行。
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable

from .config import project_root
from .security import SPECTOR_JSON, TIER1_JSON

SKILL_ROOT_CONTAINER = "/skills"
REPORTS_CONTAINER = "/app/reports"
SIMILARITY_REPORT = "skillevaluator-similarity.json"
COMPANY_CATALOG_NAME = "company-catalog.json"
COMPANY_MATCH_DIR = "company-match"
RESULTS_DIR_CONTAINER = "/app/reports/reco-results"
SECURITY_DIR_CONTAINER = "/app/reports/security"

# 命令执行器，测试时可注入。
Executor = Callable[[list[str]], int]


def company_catalog_container_path() -> str:
    return f"{REPORTS_CONTAINER}/{COMPANY_CATALOG_NAME}"


def _output_subdir(skill_rel: str) -> str:
    """把 skill 相对路径映射为报告子目录名（``/`` → ``_``）。"""
    return skill_rel.replace("/", "_")


def build_company_catalog_command(library_rel: str, full_body: bool = True) -> list[str]:
    """对公司库快照建 embedding catalog（Tier2 语义匹配的基准）。"""
    cmd = [
        "docker", "compose", "run", "--rm", "skillevaluator",
        "similarity-check", f"{SKILL_ROOT_CONTAINER}/{library_rel}",
        "--save-catalog", company_catalog_container_path(),
    ]
    if full_body:
        cmd.append("--full-body")
    return cmd


def build_company_query_command(
    skill_rel: str,
    output_subdir: str | None = None,
    full_body: bool = True,
) -> list[str]:
    """被测 skill 对公司库 catalog 语义比对，报告落到 company-match/<subdir>。"""
    subdir = output_subdir or _output_subdir(skill_rel)
    cmd = [
        "docker", "compose", "run", "--rm", "skillevaluator",
        "similarity-check", f"{SKILL_ROOT_CONTAINER}/{skill_rel}",
        "--catalog", company_catalog_container_path(),
        "--output-dir", f"{REPORTS_CONTAINER}/{COMPANY_MATCH_DIR}/{subdir}",
        "--report", "json",
    ]
    if full_body:
        cmd.append("--full-body")
    return cmd


def build_company_match_commands(
    skills: list[str],
    library_rel: str,
    full_body: bool = True,
) -> list[list[str]]:
    """先建公司库 catalog，再对每个被测 skill 分别 query。"""
    commands = [build_company_catalog_command(library_rel, full_body=full_body)]
    for skill in skills:
        commands.append(build_company_query_command(skill, full_body=full_body))
    return commands


def build_tier3_command(
    skill_rel: str,
    agent: str = "opencode",
    model: str = "qwen3.8-flash",
    max_cases: int | None = 1,
    timeout_multiplier: int | None = 3,
    results_dir: str | None = RESULTS_DIR_CONTAINER,
) -> list[str]:
    """对单个 skill 跑 Tier3（with-skill + baseline 双臂）。"""
    cmd = [
        "docker", "compose", "run", "--rm", "skillevaluator",
        "tier3", f"{SKILL_ROOT_CONTAINER}/{skill_rel}",
        "--agents", agent,
        "--model", f"openai/{model}",
    ]
    if max_cases is not None:
        cmd += ["--max-cases", str(max_cases)]
    if timeout_multiplier is not None:
        cmd += ["--timeout-multiplier", str(timeout_multiplier)]
    if results_dir is not None:
        cmd += ["--results-dir", results_dir]
    return cmd


def build_skillspector_scan_command(
    skill_rel: str,
    output_subdir: str | None = None,
    use_llm: bool = False,
) -> list[str]:
    """阶段零：对单个 skill 跑 SkillSpector 安全扫描，报告落 ``skillspector.json``。

    ``use_llm=False``（默认）为静态扫描（``--no-llm``）；``use_llm=True`` 启用
    LLM 语义分析（需网关凭据）。
    """
    subdir = output_subdir or _output_subdir(skill_rel)
    cmd = [
        "docker", "compose", "run", "--rm", "skillspector",
        "scan", f"/scan/{skill_rel}",
        "--format", "json",
        "--output", f"{SECURITY_DIR_CONTAINER}/{subdir}/{SPECTOR_JSON}",
    ]
    if not use_llm:
        cmd.append("--no-llm")
    return cmd


def build_tier1_scan_command(
    skill_rel: str,
    output_subdir: str | None = None,
    use_llm: bool = False,
) -> list[str]:
    """阶段零：对单个 skill 跑 SkillEvaluator Tier1 检查，报告落 ``skillevaluator-tier1.json``。

    ``use_llm=False``（默认）为静态检查（``--no-llm``）；``use_llm=True`` 启用
    LLM 环节（rubric_eval / 语义验证）。
    """
    subdir = output_subdir or _output_subdir(skill_rel)
    cmd = [
        "docker", "compose", "run", "--rm", "skillevaluator",
        "tier1", f"{SKILL_ROOT_CONTAINER}/{skill_rel}",
        "-r", "json",
        "-o", f"{SECURITY_DIR_CONTAINER}/{subdir}",
    ]
    if not use_llm:
        cmd.append("--no-llm")
    return cmd


def build_security_scan_commands(
    skills: list[str],
    use_llm: bool = False,
) -> list[list[str]]:
    """阶段零：对每个 skill 依次跑 SkillSpector + Tier1，产出完整 Tier1 安全证据。"""
    commands: list[list[str]] = []
    for skill in skills:
        commands.append(build_skillspector_scan_command(skill, use_llm=use_llm))
        commands.append(build_tier1_scan_command(skill, use_llm=use_llm))
    return commands


def copy_shared_evals(
    eval_source_rel: str,
    targets: list[str],
    *,
    dataset_root: Path | None = None,
    dry_run: bool = False,
) -> list[dict]:
    """把 ``<eval_source>/evals`` 的用例定义（``evals.json`` + ``files/``）复制到每个 target。

    只写 ``<target>/evals``，且仅复制用例定义（跳过 ``results/`` 等运行产物），
    覆盖以保证两者用例字节一致（Tier3 ``dataset_digest`` 相同 → 可比）。
    ``dry_run=True`` 时只生成计划不落地；源缺失时标记 ``copied=False`` + ``error``。
    """
    root = dataset_root or project_root() / "skill-dataset"
    src_dir = root / eval_source_rel / "evals"
    src_json = src_dir / "evals.json"
    src_files = src_dir / "files"
    ops: list[dict] = []
    for target in targets:
        dst_dir = root / target / "evals"
        op: dict = {"source": str(src_dir), "target": str(dst_dir), "copied": False}
        if not src_json.is_file():
            op["error"] = f"共享用例源缺失 evals.json：{src_dir}"
            ops.append(op)
            continue
        if dry_run:
            ops.append(op)
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_json, dst_dir / "evals.json")
        if src_files.is_dir():
            shutil.copytree(src_files, dst_dir / "files", dirs_exist_ok=True)
        op["copied"] = True
        ops.append(op)
    return ops


def run_pipeline(
    base_rel: str,
    candidate_rel: str,
    *,
    library_rel: str = "library-20261118",
    eval_source: str | None = None,
    agent: str = "opencode",
    model: str = "qwen3.8-flash",
    run: bool = False,
    include_security: bool = True,
    executor: Executor | None = None,
) -> dict:
    """编排新流程：阶段零安全预扫描 + 建公司库 catalog + 正向比对 + 共享用例 Tier3×2。

    返回 ``{"commands": [...], "host_ops": [...], "executed": bool}``。
    dry-run 只打印命令与待执行的共享用例复制，不落地。
    """
    host_ops = (
        copy_shared_evals(eval_source, [base_rel, candidate_rel], dry_run=not run)
        if eval_source
        else []
    )
    security = (
        build_security_scan_commands([base_rel, candidate_rel])
        if include_security
        else []
    )
    commands = [
        *security,
        build_company_catalog_command(library_rel),
        build_company_query_command(base_rel),
        build_tier3_command(base_rel, agent=agent, model=model),
        build_tier3_command(candidate_rel, agent=agent, model=model),
    ]

    if not run:
        for c in commands:
            print(" ".join(c))
        for op in host_ops:
            if op.get("copied"):
                print(f"[host] 复制共享用例 {op['source']} -> {op['target']}")
            elif op.get("error"):
                print(f"[host][warn] {op.get('error')}")
            else:
                print(f"[host] 将复制共享用例 {op['source']} -> {op['target']}")
        return {"commands": commands, "host_ops": host_ops, "executed": False}

    run_executor = executor or _shell_executor
    for c in commands:
        rc = run_executor(c)
        if rc != 0:
            return {"commands": commands, "host_ops": host_ops,
                    "executed": False, "failed_command": c, "returncode": rc}
    return {"commands": commands, "host_ops": host_ops, "executed": True}


def _shell_executor(cmd: list[str]) -> int:
    return subprocess.run(cmd).returncode
