#!/usr/bin/env python3
"""Bytebase SQL 变更提交、查询和权限申请 CLI。"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from config import load_config, get_session_path, get_bytebase_url
from auth import login_via_sso, load_session
from submit import submit_sql


def main():
    parser = argparse.ArgumentParser(
        prog="bytebase-submit",
        description="Bytebase SQL 变更提交、数据库查询和权限申请",
    )
    subparsers = parser.add_subparsers(dest="command")

    # login 子命令
    login_parser = subparsers.add_parser("login", help="通过 SSO 登录 Bytebase")
    login_parser.add_argument("--config", help="配置文件路径")

    # submit 子命令（默认）
    submit_parser = subparsers.add_parser("submit", help="提交 SQL 变更")
    submit_parser.add_argument("--project", "-p", required=True, help="Bytebase 项目名")
    submit_parser.add_argument("--database", "-d", required=True, help="目标数据库")
    submit_parser.add_argument("--sql-file", "-f", help="SQL 文件路径")
    submit_parser.add_argument("--sql", "-s", help="直接传入 SQL 语句")
    submit_parser.add_argument("--title", "-t", help="Issue 标题")
    submit_parser.add_argument("--type", choices=["DDL", "DML"], default="DDL", help="变更类型")
    submit_parser.add_argument("--label", "-l", action="append", help="Issue 标签（可多次指定，默认: 数据变更）")
    submit_parser.add_argument("--dry-run", action="store_true", help="只显示不提交")
    submit_parser.add_argument("--force-browser", action="store_true", help="强制浏览器模式")
    submit_parser.add_argument("--config", help="配置文件路径")

    # list-projects 子命令
    lp_parser = subparsers.add_parser("list-projects", help="列出可用项目")
    lp_parser.add_argument("--config", help="配置文件路径")

    # list-databases 子命令
    ld_parser = subparsers.add_parser("list-databases", help="列出项目下数据库")
    ld_parser.add_argument("--project", "-p", required=True, help="项目名")
    ld_parser.add_argument("--config", help="配置文件路径")

    # request-query 子命令
    rq_parser = subparsers.add_parser("request-query", help="申请数据库查询权限")
    rq_parser.add_argument("--project", "-p", required=True, help="Bytebase 项目名")
    rq_parser.add_argument("--database", "-d", required=True, help="目标数据库（完整路径或简称）")
    rq_parser.add_argument("--title", "-t", help="工单标题")
    rq_parser.add_argument("--expire-days", "-e", type=int, default=7, help="过期天数（默认7）")
    rq_parser.add_argument("--reason", "-r", help="申请原因")
    rq_parser.add_argument("--config", help="配置文件路径")

    query_parser = subparsers.add_parser("query", help="执行 SQL Editor 查询并返回结果")
    query_parser.add_argument("--project", "-p", help="项目名（数据库简称需要指定）")
    query_parser.add_argument("--database", "-d", help="数据库简称或完整资源路径")
    query_parser.add_argument("--sheet-url", help="SQL Editor Sheet 链接，读取数据库和已保存 SQL")
    sql_source = query_parser.add_mutually_exclusive_group()
    sql_source.add_argument("--sql", "-s", help="直接传入 SQL（覆盖 Sheet SQL）")
    sql_source.add_argument("--sql-file", "-f", help="SQL 文件（覆盖 Sheet SQL）")
    query_parser.add_argument("--limit", type=int, default=1000, help="最多返回行数（默认1000）")
    query_parser.add_argument("--schema", help="查询 schema")
    query_parser.add_argument("--data-source-id", help="指定实例上的数据源 ID")
    query_parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数（默认30，不自动重试）")
    query_parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    query_parser.add_argument("--output", "-o", help="结果保存路径（默认输出到终端）")
    query_parser.add_argument("--config", help="配置文件路径")

    args = parser.parse_args()

    # 无子命令时，检查是否有 --project 等参数（兼容不写 submit）
    if args.command is None:
        if len(sys.argv) > 1 and sys.argv[1] not in ("login", "submit", "list-projects", "list-databases", "request-query", "query", "-h", "--help"):
            # 当作 submit 处理
            sys.argv.insert(1, "submit")
            args = parser.parse_args()
        else:
            parser.print_help()
            sys.exit(1)

    config = load_config(getattr(args, "config", None))

    if args.command == "login":
        cmd_login(config)
    elif args.command == "submit":
        cmd_submit(config, args)
    elif args.command == "list-projects":
        cmd_list_projects(config)
    elif args.command == "list-databases":
        cmd_list_databases(config, args)
    elif args.command == "request-query":
        cmd_request_query(config, args)
    elif args.command == "query":
        from query import cmd_query
        cmd_query(config, args)


def cmd_login(config: dict):
    """执行 SSO 登录。"""
    base_url = get_bytebase_url(config)
    session_path = get_session_path(config)
    timeout = config["session"].get("timeout_seconds", 120)

    try:
        login_via_sso(base_url, session_path, timeout)
    except TimeoutError as e:
        print(f"\n错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n登录失败: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_submit(config: dict, args):
    """提交 SQL。"""
    # 获取 SQL 内容
    if args.sql_file:
        sql_path = Path(args.sql_file)
        if not sql_path.exists():
            print(f"错误: SQL 文件不存在: {args.sql_file}", file=sys.stderr)
            sys.exit(1)
        sql = sql_path.read_text(encoding="utf-8")
    elif args.sql:
        sql = args.sql
    else:
        print("错误: 必须指定 --sql-file 或 --sql", file=sys.stderr)
        sys.exit(1)

    # 生成默认标题
    title = args.title
    if not title:
        if args.sql_file:
            title = f"{Path(args.sql_file).stem} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            title = f"SQL Change - {datetime.now().strftime('%Y%m%d_%H%M%S')}"

    project = args.project or config["defaults"].get("project")
    if not project:
        print("错误: 必须指定 --project", file=sys.stderr)
        sys.exit(1)

    try:
        issue_url = submit_sql(
            config=config,
            project=project,
            database=args.database,
            sql=sql,
            title=title,
            change_type=args.type,
            labels=args.label,
            force_browser=args.force_browser,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            print(f"\n提交成功!")
            print(f"Issue URL: {issue_url}")
    except RuntimeError as e:
        print(f"\n错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n提交失败: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_projects(config: dict):
    """列出可用项目。"""
    from api_client import BytebaseAPIClient

    base_url = get_bytebase_url(config)
    session_path = get_session_path(config)
    session = load_session(session_path)
    if not session:
        print("错误: 未登录。请先运行: bytebase-submit login", file=sys.stderr)
        sys.exit(1)

    client = BytebaseAPIClient(base_url, session)
    projects = client.list_projects()
    if not projects:
        print("未找到项目。")
        return
    print("可用项目:")
    for p in projects:
        name = p.get("name", "").split("/")[-1]
        title = p.get("title", name)
        print(f"  {name:20s} {title}")


def cmd_list_databases(config: dict, args):
    """列出数据库。"""
    from api_client import BytebaseAPIClient

    base_url = get_bytebase_url(config)
    session_path = get_session_path(config)
    session = load_session(session_path)
    if not session:
        print("错误: 未登录。请先运行: bytebase-submit login", file=sys.stderr)
        sys.exit(1)

    client = BytebaseAPIClient(base_url, session)
    databases = client.list_databases(args.project)
    if not databases:
        print(f"项目 {args.project} 下未找到数据库。")
        return
    print(f"项目 {args.project} 的数据库:")
    for db in databases:
        name = db.get("name", "")
        env = db.get("effectiveEnvironment", "").split("/")[-1]
        engine = db.get("instanceResource", {}).get("engine", "")
        print(f"  {env:8s} {engine:12s} {name}")


def cmd_request_query(config: dict, args):
    """申请数据库查询权限。"""
    from api_client import BytebaseAPIClient
    import base64

    base_url = get_bytebase_url(config)
    session_path = get_session_path(config)
    session = load_session(session_path)
    if not session:
        print("错误: 未登录。请先运行: bytebase-submit login", file=sys.stderr)
        sys.exit(1)

    # 从 JWT 中提取用户邮箱
    token = session.get("access_token", "")
    try:
        payload_part = token.split(".")[1]
        padding = 4 - len(payload_part) % 4
        payload_part += "=" * padding
        jwt_payload = json.loads(base64.b64decode(payload_part))
        user_email = jwt_payload.get("sub", "")
    except Exception:
        user_email = ""

    if not user_email:
        print("错误: 无法从 token 中提取用户信息", file=sys.stderr)
        sys.exit(1)

    title = args.title or f"申请查询权限 - {args.database} - {datetime.now().strftime('%Y%m%d')}"

    client = BytebaseAPIClient(base_url, session)
    try:
        issue_url = client.create_query_request(
            project=args.project,
            database=args.database,
            user=user_email,
            title=title,
            expire_days=args.expire_days,
            reason=args.reason or "",
        )
        print(f"\n提交成功!")
        print(f"Issue URL: {issue_url}")
    except Exception as e:
        print(f"\n提交失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
