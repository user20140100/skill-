#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ES Log Query - 生产环境日志查询工具
支持 search_after 分页获取超过 10000 条日志
"""

import argparse
import json
import os
import re
import sys
import base64
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


def _load_env() -> Dict[str, str]:
    """从 skill 目录下的 .env 文件加载配置"""
    script_dir = Path(__file__).resolve().parent
    env_path = script_dir / '.env'
    env = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _get_es_config() -> Dict[str, str]:
    """获取 ES 配置，优先从 .env 读取"""
    env = _load_env()
    return {
        'host': env.get('ES_HOST', 'http://10.20.10.45:9200'),
        'user': env.get('ES_USER', ''),
        'password': env.get('ES_PASSWORD', ''),
        'index': env.get('ES_INDEX', 'log-sys-inner-*')
    }


def _ensure_credentials(config: Dict[str, str]) -> None:
    """检查账号密码，缺失时提示用户"""
    if not config.get('user') or not config.get('password'):
        print("错误: 需要 ES 账号密码才能查询。", file=sys.stderr)
        print("请在 skill 目录下创建 .env 文件，填写 ES_USER 和 ES_PASSWORD。", file=sys.stderr)
        print("可参考 .env.example 模板，或联系 雒小伟 获取只读账号。", file=sys.stderr)
        sys.exit(1)


# 默认配置（不含敏感信息，实际值从 .env 加载）
ES_CONFIG = _get_es_config()

# 默认 AppId 列表
DEFAULT_APP_IDS = [
    'ac98c1e3a6e447a09b8daabe',
    '072018f848c244b987bf439f'
]


def parse_query_string(query: str) -> Dict[str, Any]:
    """解析查询字符串: appId:"xxx" and message:"yyy" or traceId:"zzz" """
    filters = []
    pattern = r'(\w+):(?:"([^"]+)"|(\S+))'
    matches = re.findall(pattern, query)

    for field, quoted_val, unquoted_val in matches:
        value = quoted_val if quoted_val else unquoted_val
        if value:
            filters.append({field: value})

    return filters


def build_es_query(filters: List[Dict], time_range: str, app_ids: List[str] = None,
                   limit: int = 100, search_after: Optional[List] = None) -> Dict:
    """构建 ES 查询"""
    now = datetime.now(timezone.utc)
    if time_range.endswith('h'):
        hours = int(time_range[:-1])
        gte = (now - timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    elif time_range.endswith('d'):
        days = int(time_range[:-1])
        gte = (now - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    elif '-' in time_range and len(time_range) == 10:
        gte = f"{time_range}T00:00:00.000Z"
    else:
        gte = now.strftime('%Y-%m-%dT00:00:00.000Z')

    lte = now.strftime('%Y-%m-%dT%H:%M:%S.999Z')

    filter_list = []

    if app_ids:
        if len(app_ids) == 1:
            filter_list.append({'match_phrase': {'appId': app_ids[0]}})
        else:
            filter_list.append({'bool': {'should': [{'match_phrase': {'appId': app_id}} for app_id in app_ids], 'minimum_should_match': 1}})

    for f in filters:
        for field, value in f.items():
            if '*' in value:
                filter_list.append({'wildcard': {field: {'value': f"*{value}*"}}})
            else:
                filter_list.append({'match_phrase': {field: value}})

    filter_list.append({'range': {'@timestamp': {'gte': gte, 'lte': lte}}})

    # 使用 search_after 时必须指定 sort
    query_body = {
        'track_total_hits': False,
        'size': min(limit, 5000),
        '_source': True,
        'sort': [{'@timestamp': {'order': 'desc'}}, {'_doc': {'order': 'desc'}}],
        'query': {
            'bool': {
                'filter': filter_list
            }
        }
    }

    if search_after:
        query_body['search_after'] = search_after

    return query_body


def execute_search_after(filters: List[Dict], time_range: str, app_ids: List[str],
                         total_limit: int, config: Dict = None, output_file=None,
                         show_progress: bool = True) -> int:
    """使用 search_after 分页查询大量数据"""
    if config is None:
        config = ES_CONFIG

    credentials = f"{config['user']}:{config['password']}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    headers = {'Content-Type': 'application/json', 'Authorization': f'Basic {encoded_credentials}'}

    search_after = None
    total_hits = 0
    written_hits = 0
    page_count = 0
    batch_size = 5000

    try:
        while total_hits < total_limit:
            page_count += 1
            query_body = build_es_query(filters, time_range, app_ids, batch_size, search_after)

            request_data = json.dumps(query_body).encode('utf-8')
            req = urllib.request.Request(
                f"{config['host']}/{config['index']}/_search",
                data=request_data,
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=60, context=ssl_context) as response:
                result = json.loads(response.read().decode('utf-8'))

            hits = result.get('hits', {}).get('hits', [])
            if not hits:
                break

            last_hit = hits[-1]
            search_after = last_hit.get('sort')

            for hit in hits:
                src = hit.get('_source', {})
                timestamp = src.get('@timestamp', '')
                message = src.get('message', '')
                if output_file:
                    output_file.write(f"=== [{written_hits + 1}] {timestamp} ===\n")
                    output_file.write(message + '\n\n')
                written_hits += 1

            total_hits += len(hits)

            if show_progress:
                print(f"\r已获取: {total_hits} 条 (第 {page_count} 页)", end='', flush=True)

            if len(hits) < batch_size:
                break

        if show_progress:
            print(f"\n\n共获取: {written_hits} 条日志")

        return written_hits

    except Exception as e:
        print(f"\n查询失败: {e}", file=sys.stderr)
        sys.exit(1)


def execute_query(query_body: Dict, config: Dict = None) -> List[Dict]:
    """执行普通 ES 查询"""
    if config is None:
        config = ES_CONFIG

    credentials = f"{config['user']}:{config['password']}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    request_data = json.dumps(query_body).encode('utf-8')
    req = urllib.request.Request(
        f"{config['host']}/{config['index']}/_search",
        data=request_data,
        headers={'Content-Type': 'application/json', 'Authorization': f'Basic {encoded_credentials}'},
        method='POST'
    )

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
        return result.get('hits', {}).get('hits', [])
    except Exception as e:
        print(f"查询失败: {e}", file=sys.stderr)
        sys.exit(1)


def print_results(hits: List[Dict], keyword_filter: str = None, max_msg_len: int = 2000):
    """打印查询结果"""
    if not hits:
        print("未查询到任何日志")
        return

    print(f"\n查询到 {len(hits)} 条日志:\n")

    for i, hit in enumerate(hits, 1):
        src = hit.get('_source', {})
        timestamp = src.get('@timestamp', '')
        message = src.get('message', '')

        if keyword_filter and keyword_filter.lower() not in message.lower():
            continue

        print(f"=== [{i}] {timestamp} ===")
        print(message[:max_msg_len])
        print()


def main():
    parser = argparse.ArgumentParser(description='ES 日志查询工具 (支持 search_after 分页获取大量数据)')
    parser.add_argument('query', nargs='?', help='查询条件，如: appId:"xxx" and message:"yyy"')
    parser.add_argument('-t', '--time', default='24h', help='时间范围，如: 1h, 2h, 24h, 2026-02-27')
    parser.add_argument('-l', '--limit', type=int, default=100, help='返回结果数量 (默认 100，超过 10000 自动使用分页)')
    parser.add_argument('-k', '--keyword', help='关键词过滤')
    parser.add_argument('--index', default=ES_CONFIG['index'], help='索引名称')
    parser.add_argument('--app-id', action='append', help='指定 AppId (可多次使用)')
    parser.add_argument('--app-ids', help='指定 AppId 列表 (逗号分隔)')
    parser.add_argument('-o', '--output', help='输出到文件')

    args = parser.parse_args()

    # 获取 AppId 列表
    app_ids = None
    if args.app_id:
        app_ids = args.app_id
    elif args.app_ids:
        app_ids = args.app_ids.split(',')
    else:
        app_ids = DEFAULT_APP_IDS

    # 解析查询条件
    query_str = args.query or ""
    filters = parse_query_string(query_str)

    if not filters and query_str:
        filters = [{'message': query_str}]

    if args.index:
        ES_CONFIG['index'] = args.index

    _ensure_credentials(ES_CONFIG)

    # 打开输出文件
    output_file = None
    if args.output:
        output_file = open(args.output, 'w', encoding='utf-8')

    try:
        # 自动判断是否使用分页 (limit > 10000)
        use_pagination = args.limit > 10000

        if use_pagination:
            print(f"使用 search_after 分页查询，最多获取 {args.limit} 条...")
            execute_search_after(filters, args.time, app_ids, args.limit, output_file=output_file)
        else:
            query_body = build_es_query(filters, args.time, app_ids, args.limit)
            hits = execute_query(query_body)

            if output_file:
                for i, hit in enumerate(hits, 1):
                    src = hit.get('_source', {})
                    timestamp = src.get('@timestamp', '')
                    message = src.get('message', '')
                    output_file.write(f"=== [{i}] {timestamp} ===\n")
                    output_file.write(message + '\n\n')
                print(f"已保存 {len(hits)} 条日志到: {args.output}")
            else:
                print_results(hits, args.keyword)
    finally:
        if output_file:
            output_file.close()


if __name__ == '__main__':
    main()
