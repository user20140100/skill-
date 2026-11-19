import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def login_via_sso(bytebase_url: str, session_path: Path, timeout: int = 120) -> dict:
    """打开浏览器完成 SSO 登录，抓取 token 并缓存。"""
    session_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"正在打开浏览器，请完成 SSO 登录...")
    print(f"目标: {bytebase_url}")
    print(f"等待超时: {timeout} 秒")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(bytebase_url)
        print("浏览器已打开，请完成扫码/验证码登录...")
        print("登录成功后将自动检测并保存 session。")
        print()

        logged_in = _wait_for_login(page, bytebase_url, timeout)
        if not logged_in:
            browser.close()
            raise TimeoutError(
                f"登录超时（{timeout}秒）。请重试: bytebase-submit login"
            )

        session_data = _extract_session(context, page, bytebase_url)
        browser.close()

    session_data["created_at"] = time.time()
    session_data["bytebase_url"] = bytebase_url

    with open(session_path, "w") as f:
        json.dump(session_data, f, indent=2)

    print(f"\n登录成功! Session 已缓存到: {session_path}")
    return session_data


def _wait_for_login(page, bytebase_url: str, timeout: int) -> bool:
    """轮询等待登录完成。判定标准：access-token cookie 出现。"""
    from urllib.parse import urlparse
    target_host = urlparse(bytebase_url).hostname

    print("  等待登录完成（检测 access-token cookie）...")
    last_url = ""
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            current_url = page.url
            if current_url != last_url:
                print(f"  [页面] {current_url}")
                last_url = current_url

            # 检查 cookie 是否已经有 access-token
            context = page.context
            cookies = context.cookies()
            for cookie in cookies:
                if cookie.get("name") == "access-token" and cookie.get("value"):
                    print(f"  [成功] 检测到 access-token cookie")
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        pass
                    return True
        except Exception as e:
            print(f"  [异常] {e}")

        time.sleep(1)

    return False


def _extract_session(context, page, bytebase_url: str) -> dict:
    """从浏览器提取 cookies 和 localStorage token。"""
    from urllib.parse import urlparse
    target_host = urlparse(bytebase_url).hostname

    cookies = context.cookies()

    # 提取 localStorage 中可能的 token（带重试，防止导航中 context 销毁）
    local_storage = {}
    for attempt in range(3):
        try:
            local_storage = page.evaluate("""() => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.toLowerCase().includes('token') ||
                        key.toLowerCase().includes('auth') ||
                        key.toLowerCase().includes('session') ||
                        key.toLowerCase().includes('user')) {
                        items[key] = localStorage.getItem(key);
                    }
                }
                return items;
            }""")
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                print(f"  [警告] 无法读取 localStorage: {e}")

    # 优先从 Bytebase 域名的 cookies 找 access-token
    access_token = None
    bytebase_cookies = []
    for cookie in cookies:
        domain = cookie.get("domain", "")
        # cookie domain 可能是 ".bytebase.gz.cvte.cn" 或 "bytebase.gz.cvte.cn"
        if target_host in domain:
            bytebase_cookies.append(cookie)
            if cookie["name"] == "access-token":
                access_token = cookie["value"]

    return {
        "cookies": bytebase_cookies,
        "local_storage": local_storage,
        "access_token": access_token,
    }


def load_session(session_path: Path) -> dict | None:
    """加载缓存的 session。返回 None 如果不存在或已过期。"""
    if not session_path.exists():
        return None

    with open(session_path, "r") as f:
        data = json.load(f)

    # 简单判断：超过 4 小时认为过期（可调整）
    created_at = data.get("created_at", 0)
    if time.time() - created_at > 4 * 3600:
        print("Session 已过期（超过 4 小时）。请重新登录: bytebase-submit login")
        return None

    return data


def get_auth_headers(session: dict) -> dict:
    """从 session 中构造认证 headers。"""
    headers = {}
    if session.get("access_token"):
        headers["Authorization"] = f"Bearer {session['access_token']}"
    return headers


def get_auth_cookies(session: dict) -> dict:
    """从 session 中构造 cookies dict（用于 requests）。"""
    cookies = {}
    for cookie in session.get("cookies", []):
        cookies[cookie["name"]] = cookie["value"]
    return cookies
