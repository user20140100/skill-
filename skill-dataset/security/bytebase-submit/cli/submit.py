from pathlib import Path
from api_client import BytebaseAPIClient, AuthExpiredError
from browser_client import BytebaseBrowserClient, SessionExpiredError
from auth import load_session
from config import get_session_path, get_bytebase_url


def submit_sql(
    config: dict,
    project: str,
    database: str,
    sql: str,
    title: str,
    change_type: str = "DDL",
    labels: list[str] = None,
    force_browser: bool = False,
    dry_run: bool = False,
) -> str:
    """提交 SQL 到 Bytebase。返回 Issue URL。"""
    base_url = get_bytebase_url(config)
    session_path = get_session_path(config)

    if dry_run:
        print("\n[DRY RUN] 以下内容将被提交:")
        print(f"  URL:      {base_url}")
        print(f"  项目:     {project}")
        print(f"  数据库:   {database}")
        print(f"  类型:     {change_type}")
        print(f"  标题:     {title}")
        print(f"  SQL 长度: {len(sql)} 字符")
        print(f"  SQL 预览: {sql[:200]}{'...' if len(sql) > 200 else ''}")
        return "[DRY RUN]"

    # 加载 session
    session = load_session(session_path)
    if not session:
        raise RuntimeError(
            "未找到有效 session。请先登录: bytebase-submit login"
        )

    # 尝试 API 模式
    if not force_browser:
        try:
            client = BytebaseAPIClient(base_url, session)
            if client.check_api_available():
                print("使用 API 模式提交...")
                return client.submit(project, database, sql, title, change_type, labels)
            else:
                print("API 不可用，降级到浏览器模式...")
        except AuthExpiredError:
            raise
        except Exception as e:
            print(f"API 提交失败 ({e})，降级到浏览器模式...")

    # Playwright 浏览器模式
    print("使用浏览器自动化模式提交...")
    browser_client = BytebaseBrowserClient(base_url, session)
    return browser_client.submit(project, database, sql, title, change_type)
