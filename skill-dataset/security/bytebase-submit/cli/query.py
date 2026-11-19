"""Bytebase SQL Editor 查询和结果输出。"""

import base64
import csv
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from api_client import BytebaseAPIClient
from auth import load_session
from config import get_bytebase_url, get_session_path


def parse_sheet_url(url, base_url):
    target, base = urlsplit(url), urlsplit(base_url)
    match = re.fullmatch(r"/sql-editor/projects/([^/]+)/sheets/(\d+)/?", target.path)
    if (target.scheme, target.netloc) != (base.scheme, base.netloc) or not match:
        raise ValueError("--sheet-url 必须是当前 Bytebase 站点的 SQL Editor Sheet 链接")
    return unquote(match[1]), match[2]


def resolve_database(client, database, project):
    if re.fullmatch(r"instances/[^/]+/databases/[^/]+", database):
        return client._request("GET", f"/v1/{quote(database, safe='/')}").json()
    if "/" in database or not project:
        raise ValueError("使用数据库简称时必须提供 --project，或使用完整数据库资源路径")
    matches = []
    page_token = ""
    seen = set()
    while True:
        data = client._request(
            "GET", f"/v1/projects/{quote(project, safe='')}/databases",
            params={"pageSize": 1000, "pageToken": page_token},
        ).json()
        matches.extend(d for d in data.get("databases", [])
                       if d.get("name", "").rsplit("/", 1)[-1] == database
                       and d.get("state") != "DELETED")
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break
        if page_token in seen:
            raise ValueError("数据库列表分页异常：重复 page token")
        seen.add(page_token)
    if not matches:
        raise ValueError(f"项目 {project} 下未找到数据库 {database}")
    if len(matches) != 1:
        names = ", ".join(d["name"] for d in matches)
        raise ValueError(f"存在同名数据库，请使用完整路径: {names}")
    return matches[0]


def select_data_source(client, database, data_source_id=None):
    resource = database.get("instanceResource", {})
    sources = resource.get("dataSources", [])
    if not sources:
        instance = database["name"].split("/databases/", 1)[0]
        sources = client._request("GET", f"/v1/{quote(instance, safe='/')}").json().get("dataSources", [])
    if data_source_id:
        if not any(s.get("id") == data_source_id for s in sources):
            raise ValueError("指定的 data-source-id 不属于目标数据库实例")
        return data_source_id
    for source_type in ("READ_ONLY", "ADMIN"):
        choices = [s for s in sources if s.get("type") == source_type and s.get("id")]
        if len(choices) == 1:
            return choices[0]["id"]
        if len(choices) > 1:
            raise ValueError("存在多个查询数据源，请使用 --data-source-id 指定")
    raise ValueError("没有可用查询数据源")


def decode_value(value):
    if not value or "nullValue" in value:
        return None
    for key in ("int32Value", "int64Value", "uint32Value", "uint64Value"):
        if key in value:
            return int(value[key])
    for key in ("boolValue", "doubleValue", "floatValue", "stringValue", "bytesValue", "valueValue"):
        if key in value:
            return value[key]
    for key in ("timestampValue", "timestampTzValue"):
        if key in value:
            # 保留时区、精度等元数据，避免时间戳转换丢失信息。
            return value[key]
    raise ValueError(f"无法识别 Bytebase 单元格类型: {', '.join(value)}")


def normalize_results(response):
    if response.get("error"):
        raise RuntimeError(response["error"])
    if not response.get("results"):
        raise RuntimeError("Bytebase 未返回查询结果")
    results = []
    for result in response["results"]:
        if result.get("error"):
            raise RuntimeError(result["error"])
        for key in ("permissionDenied", "syntaxError", "postgresError"):
            if key in result:
                raise RuntimeError(f"查询失败 ({key}): {json.dumps(result[key], ensure_ascii=False)}")
        normalized = dict(result)
        normalized["rows"] = [[decode_value(v) for v in row.get("values", [])]
                              for row in result.get("rows", [])]
        normalized["rowsCount"] = int(result.get("rowsCount", len(normalized["rows"])))
        results.append(normalized)
    return results


def cell_text(value):
    if value is None:
        return "NULL"
    if isinstance(value, (dict, list, bool)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def render_results(results, format_name):
    if format_name == "json":
        return json.dumps({"results": results}, ensure_ascii=False, indent=2) + "\n"
    if format_name == "csv":
        if len(results) != 1:
            raise ValueError("CSV 只支持单个结果集，请改用 --format json")
        result = results[0]
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(result.get("columnNames", []))
        writer.writerows(["" if v is None else cell_text(v) for v in row]
                         for row in result["rows"])
        return stream.getvalue()
    blocks = []
    for i, result in enumerate(results, 1):
        # 对齐只控制展示，不截断查询数据；保留重复列名。
        rows = [result.get("columnNames", [])] + result["rows"]
        display = [[cell_text(v).replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
                    for v in row] for row in rows]
        width = max((len(row) for row in display), default=0)
        sizes = [max((len(row[j]) for row in display if len(row) > j), default=0)
                 for j in range(width)]
        lines = [" | ".join(v.ljust(sizes[j]) for j, v in enumerate(row)) for row in display]
        if lines:
            lines.insert(1, "-+-".join("-" * n for n in sizes))
        blocks.append(f"结果集 {i}\n" + "\n".join(lines)
                      + f"\n{len(result['rows'])} 行，耗时 {result.get('latency', '未知')}\n")
    return "\n".join(blocks)


def cmd_query(config, args):
    try:
        if args.limit <= 0 or args.limit > 2147483647 or args.timeout <= 0:
            raise ValueError("limit 必须是正 int32，timeout 必须大于 0")
        if args.sql is not None and args.sql_file is not None:
            raise ValueError("--sql 和 --sql-file 不能同时使用")
        base_url = get_bytebase_url(config)
        session = load_session(get_session_path(config))
        if not session:
            raise RuntimeError("未登录或会话过期，请先运行: python3 cli.py login")
        client = BytebaseAPIClient(base_url, session)
        database, project = args.database, args.project
        worksheet = None
        if args.sheet_url:
            sheet_project, sheet_id = parse_sheet_url(args.sheet_url, base_url)
            if project and project != sheet_project:
                raise ValueError("--project 与 Sheet 链接中的项目不一致")
            project = sheet_project
            worksheet = client.get_worksheet(sheet_id)
            if worksheet.get("project") != f"projects/{project}":
                raise ValueError("Worksheet 实际所属项目与链接不一致")
            database = database or worksheet.get("database")
        if not database:
            raise ValueError("请指定 --database，或提供绑定了数据库的 --sheet-url")
        if args.sql_file:
            sql = Path(args.sql_file).read_text(encoding="utf-8")
        elif args.sql is not None:
            sql = args.sql
        elif worksheet is not None:
            sql = base64.b64decode(worksheet.get("content", ""), validate=True).decode("utf-8")
        else:
            raise ValueError("必须指定 --sql、--sql-file 或 --sheet-url")
        if not sql.strip():
            raise ValueError("SQL 为空；该 Worksheet 可能尚未保存 SQL，请使用 --sql 或 --sql-file")
        database_resource = resolve_database(client, database, project)
        if project and database_resource.get("project") != f"projects/{project}":
            raise ValueError("目标数据库不属于指定项目")
        database = database_resource["name"]
        source = select_data_source(client, database_resource, args.data_source_id)
        response = client.query(database, sql, source, args.limit, args.schema, args.timeout)
        results = normalize_results(response)
        output = render_results(results, args.format)
        for result in results:
            if len(result["rows"]) >= args.limit:
                print(f"提示: 返回行数达到限制 {args.limit}，结果可能未完整。", file=sys.stderr)
            for message in result.get("messages", []):
                print(f"[{message.get('level', 'INFO')}] {message.get('content', '')}", file=sys.stderr)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8", newline="")
            print(f"查询结果已保存: {args.output}", file=sys.stderr)
        else:
            print(output, end="")
    except Exception as exc:
        print(f"查询失败: {exc}", file=sys.stderr)
        raise SystemExit(1)
