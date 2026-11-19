import time
from playwright.sync_api import sync_playwright
from auth import get_auth_cookies


class BytebaseBrowserClient:
    """Playwright 浏览器自动化客户端（降级方案）。"""

    def __init__(self, base_url: str, session: dict):
        self.base_url = base_url
        self.session = session
        self.cookies = session.get("cookies", [])

    def submit(
        self,
        project: str,
        database: str,
        sql: str,
        title: str,
        change_type: str = "DDL",
    ) -> str:
        """通过浏览器自动化提交 SQL 变更。返回 Issue URL。"""
        print("  使用浏览器自动化模式提交...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            # 注入已有 cookies（免登录）
            if self.cookies:
                context.add_cookies(self.cookies)

            page = context.new_page()

            # 导航到项目
            project_url = f"{self.base_url}/projects/{project}"
            page.goto(project_url)
            page.wait_for_load_state("networkidle", timeout=15000)

            # 检查是否需要重新登录
            if "/auth" in page.url or "/login" in page.url:
                browser.close()
                raise SessionExpiredError(
                    "Session 已过期，请重新登录: bytebase-submit login"
                )

            # 点击新建 Issue
            issue_url = self._create_issue(page, project, database, sql, title, change_type)

            browser.close()
            return issue_url

    def _create_issue(
        self, page, project: str, database: str, sql: str, title: str, change_type: str
    ) -> str:
        """在项目页面创建新 Issue。"""
        # 点击 "New Issue" 或类似按钮
        new_issue_btn = page.query_selector(
            'button:has-text("New Issue"), '
            'a:has-text("New Issue"), '
            'button:has-text("新建"), '
            'a:has-text("新建")'
        )
        if not new_issue_btn:
            # 尝试通过 URL 直接导航
            page.goto(f"{self.base_url}/projects/{project}/issues/new")
            page.wait_for_load_state("networkidle", timeout=15000)
        else:
            new_issue_btn.click()
            page.wait_for_load_state("networkidle", timeout=15000)

        # 选择变更类型
        self._select_change_type(page, change_type)

        # 填写标题
        title_input = page.query_selector(
            'input[placeholder*="title"], '
            'input[placeholder*="标题"], '
            'input[name="title"]'
        )
        if title_input:
            title_input.fill(title)

        # 选择数据库
        self._select_database(page, database)

        # 填写 SQL
        self._fill_sql(page, sql)

        # 提交
        submit_btn = page.query_selector(
            'button:has-text("Create"), '
            'button:has-text("Submit"), '
            'button:has-text("创建"), '
            'button:has-text("提交")'
        )
        if submit_btn:
            submit_btn.click()
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)

        issue_url = page.url
        print(f"  Issue URL: {issue_url}")
        return issue_url

    def _select_change_type(self, page, change_type: str):
        """选择变更类型 DDL/DML。"""
        type_selector = page.query_selector(
            f'[data-value="{change_type}"], '
            f'label:has-text("{change_type}"), '
            f'button:has-text("{change_type}")'
        )
        if type_selector:
            type_selector.click()
            time.sleep(0.5)

    def _select_database(self, page, database: str):
        """选择目标数据库。"""
        # 尝试找到数据库选择器并选择
        db_selector = page.query_selector(
            '[class*="database"], '
            '[data-testid*="database"], '
            'select[name*="database"]'
        )
        if db_selector:
            db_selector.click()
            time.sleep(0.5)
            # 在下拉中搜索数据库名
            option = page.query_selector(f'[title*="{database}"], li:has-text("{database}")')
            if option:
                option.click()
                time.sleep(0.5)

    def _fill_sql(self, page, sql: str):
        """填写 SQL 内容。"""
        # Bytebase 使用 Monaco Editor 或 CodeMirror
        # 尝试多种方式填入 SQL
        editor = page.query_selector(
            '.monaco-editor textarea, '
            '.CodeMirror textarea, '
            'textarea[placeholder*="SQL"], '
            'textarea[class*="sql"]'
        )
        if editor:
            editor.fill(sql)
        else:
            # Monaco Editor 需要通过 JS 设置
            page.evaluate(f"""() => {{
                const editor = window.monaco?.editor?.getEditors?.()[0];
                if (editor) {{
                    editor.setValue({repr(sql)});
                    return;
                }}
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue({repr(sql)});
                    return;
                }}
                const textarea = document.querySelector('textarea');
                if (textarea) {{
                    textarea.value = {repr(sql)};
                    textarea.dispatchEvent(new Event('input', {{bubbles: true}}));
                }}
            }}""")


class SessionExpiredError(Exception):
    pass
