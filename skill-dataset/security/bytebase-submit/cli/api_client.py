import requests
import uuid
import base64
import urllib3
import sys
from auth import get_auth_headers, get_auth_cookies

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BytebaseAPIClient:
    """Bytebase v3 REST API 客户端。"""

    def __init__(self, base_url: str, session: dict):
        self.base_url = base_url
        self.session = session
        self.cookies = get_auth_cookies(session)
        token = session.get("access_token")
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        resp = requests.request(
            method,
            url,
            headers=self.headers,
            cookies=self.cookies,
            verify=False,
            timeout=kwargs.pop("timeout", 30),
            proxies={"http": None, "https": None},
            **kwargs,
        )
        if resp.status_code == 401:
            raise AuthExpiredError("Session 已过期，请重新登录: bytebase-submit login")
        if not resp.ok:
            print(f"  [API 错误] {resp.status_code} {method} {path}", file=sys.stderr)
            print(f"  [响应内容] {resp.text[:500]}", file=sys.stderr)
        resp.raise_for_status()
        return resp

    def check_api_available(self) -> bool:
        """探测 API 是否可用。"""
        try:
            resp = requests.get(
                f"{self.base_url}/v1/actuator/info",
                verify=False,
                timeout=5,
                proxies={"http": None, "https": None},
            )
            return resp.status_code == 200
        except Exception:
            return False

    def list_projects(self) -> list:
        """列出当前用户可访问的项目。"""
        projects = []
        page_token = ""
        seen = set()
        while True:
            data = self._request("POST", "/v1/projects:search", json={
                "pageSize": 1000, "pageToken": page_token,
            }).json()
            projects.extend(data.get("projects", []))
            page_token = data.get("nextPageToken", "")
            if not page_token:
                return projects
            if page_token in seen:
                raise RuntimeError("项目列表分页异常：重复 page token")
            seen.add(page_token)

    def list_databases(self, project: str) -> list:
        """列出项目下的数据库。"""
        resp = self._request("GET", f"/v1/projects/{project}/databases")
        return resp.json().get("databases", [])

    def create_sheet(self, project: str, sql: str, title: str = "") -> str:
        """创建 Sheet（上传 SQL 内容），返回 sheet name。"""
        content_b64 = base64.b64encode(sql.encode("utf-8")).decode("utf-8")
        payload = {
            "title": title or "Auto-submitted SQL",
            "content": content_b64,
        }
        resp = self._request("POST", f"/v1/projects/{project}/sheets", json=payload)
        data = resp.json()
        return data.get("name", "")

    def get_worksheet(self, worksheet_id: str) -> dict:
        """SQL Editor 的 sheets 链接实际对应 Worksheet 资源。"""
        if not str(worksheet_id).isdigit():
            raise ValueError("Worksheet ID 必须是数字")
        return self._request("GET", f"/v1/worksheets/{worksheet_id}").json()

    def query(self, database: str, sql: str, data_source_id: str,
              limit: int = 1000, schema: str = None, timeout: int = 30) -> dict:
        """通过普通 SQL Editor Query 接口查询，权限和 SQL 校验由 Bytebase 执行。"""
        import re
        from urllib.parse import quote

        if not re.fullmatch(r"instances/[^/]+/databases/[^/]+", database):
            raise ValueError("查询需要完整数据库资源路径")
        if not sql.strip():
            raise ValueError("SQL 不能为空")
        if not 1 <= limit <= 2147483647 or timeout <= 0:
            raise ValueError("limit 必须是正 int32，timeout 必须大于 0")
        if not data_source_id:
            raise ValueError("缺少查询数据源 ID")
        payload = {"name": database, "statement": sql, "limit": limit,
                   "dataSourceId": data_source_id}
        if schema is not None:
            payload["schema"] = schema
        path = f"/v1/{quote(database, safe='/')}:query"
        return self._request("POST", path, json=payload, timeout=timeout).json()

    def create_plan(
        self,
        project: str,
        database: str,
        sheet_name: str,
        title: str,
        change_type: str = "DDL",
    ) -> str:
        """创建 Plan，返回 plan name。"""
        spec_id = str(uuid.uuid4())

        if "/" not in database:
            database = f"instances/-/databases/{database}"

        # Bytebase 枚举: MIGRATE=DDL/通用, MIGRATE_SDL=SDL
        # DML 也用 MIGRATE，Bytebase 根据 SQL 内容自动判断审批流
        type_map = {"DDL": "MIGRATE", "DML": "MIGRATE"}
        db_change_type = type_map.get(change_type.upper(), "MIGRATE")

        plan_payload = {
            "title": title,
            "specs": [
                {
                    "id": spec_id,
                    "changeDatabaseConfig": {
                        "targets": [database],
                        "sheet": sheet_name,
                        "type": db_change_type,
                    },
                }
            ],
        }

        resp = self._request(
            "POST", f"/v1/projects/{project}/plans", json=plan_payload
        )
        data = resp.json()
        return data.get("name", "")

    def create_rollout(self, project: str, plan_name: str) -> str:
        """基于 Plan 创建 Rollout，返回 rollout name。"""
        resp = self._request(
            "POST", f"/v1/projects/{project}/rollouts", json={"plan": plan_name}
        )
        data = resp.json()
        return data.get("name", "")

    def create_issue(self, project: str, plan_name: str, title: str, labels: list[str] = None) -> str:
        """基于 Plan 创建 Issue，返回 issue name。"""
        issue_payload = {
            "title": title,
            "type": "DATABASE_CHANGE",
            "plan": plan_name,
            "labels": labels or ["数据变更"],
        }
        resp = self._request(
            "POST", f"/v1/projects/{project}/issues", json=issue_payload
        )
        data = resp.json()
        return data.get("name", "")

    def submit(
        self,
        project: str,
        database: str,
        sql: str,
        title: str,
        change_type: str = "DDL",
        labels: list[str] = None,
    ) -> str:
        """完整提交流程: Sheet → Plan → Issue。返回 Issue URL。"""
        print(f"  创建 Sheet...")
        sheet_name = self.create_sheet(project, sql, title)
        print(f"  Sheet: {sheet_name}")

        print(f"  创建 Plan...")
        plan_name = self.create_plan(
            project, database, sheet_name, title, change_type
        )
        print(f"  Plan: {plan_name}")

        print(f"  创建 Rollout...")
        rollout_name = self.create_rollout(project, plan_name)
        print(f"  Rollout: {rollout_name}")

        print(f"  创建 Issue...")
        issue_name = self.create_issue(project, plan_name, title, labels)
        print(f"  Issue: {issue_name}")

        issue_url = f"{self.base_url}/{issue_name}"
        return issue_url


    def create_query_request(
        self,
        project: str,
        database: str,
        user: str,
        title: str,
        expire_days: int = 7,
        reason: str = "",
    ) -> str:
        """创建查询权限申请 Issue，返回 Issue URL。"""
        from datetime import datetime, timedelta, timezone

        expire_time = (datetime.now(timezone.utc) + timedelta(days=expire_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

        if "/" not in database:
            database = f"instances/-/databases/{database}"

        if not user.startswith("users/"):
            user = f"users/{user}"

        issue_payload = {
            "title": title,
            "type": "GRANT_REQUEST",
            "description": reason or title,
            "grantRequest": {
                "role": "roles/QUERIER",
                "user": user,
                "condition": {
                    "expression": f'request.time < timestamp("{expire_time}") && resource.database == "{database}"'
                },
            },
        }

        print(f"  创建查询权限申请...")
        resp = self._request("POST", f"/v1/projects/{project}/issues", json=issue_payload)
        data = resp.json()
        issue_name = data.get("name", "")
        print(f"  Issue: {issue_name}")
        return f"{self.base_url}/{issue_name}"


class AuthExpiredError(Exception):
    pass
