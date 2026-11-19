#!/usr/bin/env python3
"""Fetch MR code review suggestions from API. Cross-platform (macOS/Windows/Linux)."""

import json
import ssl
import sys
import os
from pathlib import Path
from urllib.request import Request, urlopen, HTTPRedirectHandler, build_opener, HTTPSHandler
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError


def find_config():
    """Walk up from cwd to find .mr-suggestion.json."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        config_path = parent / ".mr-suggestion.json"
        if config_path.is_file():
            return config_path
    return None


def _create_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class _AuthRedirectHandler(HTTPRedirectHandler):
    """Preserve AUTHORIZATION header across redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is not None:
            auth = req.get_header("Authorization") or req.get_header("AUTHORIZATION")
            if auth:
                new_req.add_unredirected_header("AUTHORIZATION", auth)
        return new_req


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_suggestions.py <mr_iid> [page_size] [status]", file=sys.stderr)
        sys.exit(1)

    mr_iid = sys.argv[1]
    page_size_override = sys.argv[2] if len(sys.argv) > 2 else None
    status_override = sys.argv[3] if len(sys.argv) > 3 else None

    config_path = find_config()
    if not config_path:
        print(json.dumps({"error": "配置文件 .mr-suggestion.json 未找到，请在项目根目录创建"}), file=sys.stderr)
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    api_base_url = config.get("api_base_url", "")
    auth_token = config.get("auth_token", "")
    project_id = config.get("project_id", "")
    page_size = page_size_override or str(config.get("page_size", 10))
    status = status_override or config.get("status", "open")

    for name, value in [("api_base_url", api_base_url), ("auth_token", auth_token), ("project_id", project_id)]:
        if not value:
            print(json.dumps({"error": f"{name} 未配置"}), file=sys.stderr)
            sys.exit(1)

    params = urlencode({
        "project_id": project_id,
        "page_size": page_size,
        "status": status,
        "mr_iid": mr_iid,
    })
    url = f"{api_base_url}?{params}"

    ctx = _create_ssl_context()
    opener = build_opener(HTTPSHandler(context=ctx), _AuthRedirectHandler)
    req = Request(url, headers={"AUTHORIZATION": f"token {auth_token}"})
    try:
        with opener.open(req) as resp:
            data = resp.read().decode("utf-8")
            json.loads(data)  # validate JSON
            sys.stdout.buffer.write(data.encode("utf-8"))
            sys.stdout.buffer.write(b"\n")
    except HTTPError as e:
        print(json.dumps({"error": f"API 请求失败: {e.code} {e.reason}"}), file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(json.dumps({"error": f"网络错误: {e.reason}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
