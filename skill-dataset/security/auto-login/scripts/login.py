#!/usr/bin/env python3
"""auto-login: 打开浏览器让用户登录目标 origin，拿到 JWT 和 cookie token。

用法：
    python login.py <origin> [--force] [--no-prompt]

成功时 stdout 输出一行 JSON：{"jwt": "...", "cookie_token": "...", "cookie_name": "..."}
stderr 输出过程日志。
"""
from __future__ import annotations

import argparse
import base64
import http.client
import json
import re
import ssl
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SKILL_DIR / ".cache"
PROFILE_DIR = SKILL_DIR / ".profile"
TOKEN_PATH_IN_RESPONSE = ("data", "data", "token")
STATUS_PATH_IN_RESPONSE = ("data", "status")
GETJWT_PATH = "/api/auth/getJwtByToken"

COOKIE_TOKEN_PATTERNS = [
    re.compile(r"^x-auth-token", re.IGNORECASE),
    re.compile(r".*cmes.*info$", re.IGNORECASE),
]


def log(msg: str) -> None:
    print(f"[auto-login] {msg}", file=sys.stderr, flush=True)


def host_of(origin: str) -> str:
    p = urlparse(origin)
    if not p.scheme or not p.netloc:
        raise SystemExit(f"非法 origin: {origin!r}（需要形如 https://host）")
    return p.netloc


def cache_file(origin: str) -> Path:
    return CACHE_DIR / f"{host_of(origin)}.json"


def jwt_exp(token: str) -> int:
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return int(payload.get("exp", 0))
    except Exception:
        return 0


def read_cache(origin: str) -> dict | None:
    f = cache_file(origin)
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def write_cache(origin: str, jwt: str, cookie_token: str, cookie_name: str, extra_headers: dict | None = None) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "origin": origin,
        "jwt": jwt,
        "cookie_token": cookie_token,
        "cookie_name": cookie_name,
        "exp": jwt_exp(jwt),
        "fetched_at": int(time.time()),
    }
    if extra_headers:
        for k in ("x-jwt-type", "x-current-user-type", "x-user-type-value"):
            if k in extra_headers:
                data[k] = extra_headers[k]
    cache_file(origin).write_text(json.dumps(data, ensure_ascii=False, indent=2))


def dig(obj, path):
    for k in path:
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def extract_jwt_and_headers(resp_json: dict) -> dict:
    """返回 {"jwt": "...", "x-jwt-type": ..., "x-current-user-type": ..., "x-user-type-value": ...}"""
    status = dig(resp_json, STATUS_PATH_IN_RESPONSE)
    if str(status) != "0":
        raise RuntimeError(f"接口返回 status={status!r}，响应={json.dumps(resp_json, ensure_ascii=False)[:500]}")
    data_obj = dig(resp_json, ("data", "data"))
    if not isinstance(data_obj, dict):
        raise RuntimeError(f"响应中找不到 data.data：{json.dumps(resp_json, ensure_ascii=False)[:500]}")
    token = data_obj.get("token")
    if not token or not isinstance(token, str):
        raise RuntimeError(f"响应中找不到 token：{json.dumps(resp_json, ensure_ascii=False)[:500]}")
    result = {"jwt": token}
    for key in ("x-jwt-type", "x-current-user-type", "x-user-type-value"):
        camel = key.replace("-", "")
        val = data_obj.get(key) or data_obj.get(camel)
        if val:
            result[key] = str(val)
    return result


def find_cookie_token(cookies: list[dict]) -> tuple[str, str]:
    """从 cookie 列表中找 UUID 格式的 auth token，返回 (cookie_name, cookie_value)。"""
    for c in cookies:
        name = c.get("name", "")
        for pat in COOKIE_TOKEN_PATTERNS:
            if pat.match(name):
                value = c.get("value", "")
                if value:
                    return name, value
    return "", ""


def _call_getjwt_http_client(origin: str, cookies: list[dict]) -> dict:
    """http.client 回退：当 requests/urllib3 SSL 握手失败时使用。"""
    parsed = urlparse(origin)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    log(f"[fallback] 使用 http.client 调用 GET {origin}{GETJWT_PATH}")
    conn_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(host, port, timeout=15, context=ctx if parsed.scheme == "https" else None)
    try:
        conn.request("GET", GETJWT_PATH, headers={
            "Accept": "application/json",
            "User-Agent": "auto-login-skill/1.0",
            "Cookie": cookie_str,
            "Host": host,
        })
        resp = conn.getresponse()
        body = resp.read().decode()
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}: {body[:500]}")
        return extract_jwt_and_headers(json.loads(body))
    finally:
        conn.close()


def call_getjwt_with_cookies(origin: str, cookies: list[dict]) -> dict:
    """返回 {"jwt": "...", "x-jwt-type": ..., ...}"""
    jar = requests.cookies.RequestsCookieJar()
    host = host_of(origin)
    for c in cookies:
        domain = (c.get("domain") or "").lstrip(".")
        if domain and not (host == domain or host.endswith("." + domain)):
            continue
        jar.set(c["name"], c["value"], domain=c.get("domain") or host, path=c.get("path") or "/")
    log(f"调用 GET {origin}{GETJWT_PATH}")
    try:
        r = requests.get(
            origin.rstrip("/") + GETJWT_PATH,
            cookies=jar,
            timeout=15,
            verify=False,
            headers={"Accept": "application/json", "User-Agent": "auto-login-skill/1.0"},
        )
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
        return extract_jwt_and_headers(r.json())
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
        log(f"requests SSL/连接失败，回退到 http.client（{str(e)[:60]}）")
        return _call_getjwt_http_client(origin, cookies)


def output_result(jwt: str, cookie_token: str, cookie_name: str, extra_headers: dict | None = None) -> None:
    result = {
        "jwt": jwt,
        "cookie_token": cookie_token,
        "cookie_name": cookie_name,
    }
    if extra_headers:
        for k in ("x-jwt-type", "x-current-user-type", "x-user-type-value"):
            if k in extra_headers:
                result[k] = extra_headers[k]
    print(json.dumps(result, ensure_ascii=False))


def interactive_login(origin: str, poll_mode: bool = False) -> tuple[str, str, str, dict]:
    """返回 (jwt, cookie_token, cookie_name, extra_headers)。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("缺少 playwright，请先：pip install -r scripts/requirements.txt && python -m playwright install chromium")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        log(f"启动浏览器（持久化 profile: {PROFILE_DIR}）")
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
        )
        try:
            page = ctx.new_page() if not ctx.pages else ctx.pages[0]
            log(f"打开 {origin}，请在浏览器中完成登录")
            page.goto(origin, wait_until="domcontentloaded", timeout=60_000)

            if poll_mode:
                log("轮询模式：每 3 秒尝试调用接口，登录成功后自动完成（超时 5 分钟）")
                jwt_info = _poll_until_success(origin, ctx, timeout=300)
            else:
                if not sys.stdin.isatty():
                    raise SystemExit("当前 stdin 非交互终端，无法等待用户回车确认登录；请加 --poll 使用轮询模式。")
                try:
                    input("[auto-login] 登录完成后请回到终端按回车继续… ")
                except (EOFError, KeyboardInterrupt):
                    raise SystemExit("用户取消")
                cookies = ctx.cookies()
                jwt_info = call_getjwt_with_cookies(origin, cookies)

            cookies = ctx.cookies()
        finally:
            ctx.close()

    cookie_name, cookie_token = find_cookie_token(cookies)
    if not cookie_token:
        log("警告：未在 cookie 中找到 x-auth-token-* 或 *cmes*info 字段")
    extra_headers = {k: v for k, v in jwt_info.items() if k != "jwt"}
    return jwt_info["jwt"], cookie_token, cookie_name, extra_headers


def _poll_until_success(origin: str, ctx, timeout: int = 300) -> dict:
    """每 3 秒用当前浏览器 cookie 调接口，成功即返回 jwt_info dict。"""
    import time as _time
    deadline = _time.time() + timeout
    last_err = ""
    while _time.time() < deadline:
        _time.sleep(3)
        try:
            cookies = ctx.cookies()
            return call_getjwt_with_cookies(origin, cookies)
        except Exception as e:
            err_msg = str(e)
            if err_msg != last_err:
                log(f"等待登录… ({err_msg[:80]})")
                last_err = err_msg
    raise RuntimeError(f"轮询超时（{timeout}s），用户未完成登录")


def try_silent(origin: str) -> tuple[str, str, str, dict] | None:
    """用持久化 profile 无头尝试。返回 (jwt, cookie_token, cookie_name, extra_headers) 或 None。"""
    if not PROFILE_DIR.exists():
        return None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
        )
        try:
            page = ctx.new_page() if not ctx.pages else ctx.pages[0]
            page.goto(origin, wait_until="domcontentloaded", timeout=20_000)
            cookies = ctx.cookies()
        finally:
            ctx.close()
    jwt_info = call_getjwt_with_cookies(origin, cookies)
    cookie_name, cookie_token = find_cookie_token(cookies)
    extra_headers = {k: v for k, v in jwt_info.items() if k != "jwt"}
    return jwt_info["jwt"], cookie_token, cookie_name, extra_headers


def main():
    ap = argparse.ArgumentParser(description="登录目标 origin 并取 JWT + cookie token")
    ap.add_argument("origin", help="目标 origin，如 https://cmes-fat.gz.cvte.cn")
    ap.add_argument("--force", action="store_true", help="忽略缓存，强制重新登录")
    ap.add_argument("--poll", action="store_true", help="非交互模式：打开浏览器后轮询接口直到登录成功（适配 Claude Code 等非 tty 环境）")
    ap.add_argument("--no-prompt", action="store_true", help="不命中缓存且不能交互时直接报错退出")
    args = ap.parse_args()

    origin = args.origin.rstrip("/")
    host_of(origin)

    if not args.force:
        cached = read_cache(origin)
        if cached and cached.get("jwt"):
            remain = cached.get("exp", 0) - int(time.time())
            if remain > 60:
                log(f"命中缓存（剩余 {remain}s）")
                extra = {k: cached[k] for k in ("x-jwt-type", "x-current-user-type", "x-user-type-value") if cached.get(k)}
                output_result(cached["jwt"], cached.get("cookie_token", ""), cached.get("cookie_name", ""), extra)
                return
            log(f"缓存已过期或即将过期（剩余 {remain}s），重新登录")

    if args.no_prompt:
        raise SystemExit("缓存未命中且 --no-prompt，拒绝起浏览器")

    poll_mode = args.poll or not sys.stdin.isatty()
    jwt, cookie_token, cookie_name, extra_headers = interactive_login(origin, poll_mode=poll_mode)
    write_cache(origin, jwt, cookie_token, cookie_name, extra_headers)
    log("登录成功，token 已缓存。请求时需携带以下 header：")
    log(f"  x-auth-token: {jwt[:20]}...{jwt[-10:]}")
    if cookie_token:
        log(f"  Cookie: {cookie_name}={cookie_token}")
    for k in ("x-jwt-type", "x-current-user-type", "x-user-type-value"):
        if k in extra_headers:
            log(f"  {k}: {extra_headers[k]}")
    output_result(jwt, cookie_token, cookie_name, extra_headers)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"[auto-login] 失败: {e}", file=sys.stderr)
        sys.exit(1)
