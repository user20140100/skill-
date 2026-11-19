---
name: auto-login
description: >-
  通过 playwright 打开浏览器让用户登录指定域名，登录完成后调用 /api/auth/getJwtByToken 拿到 JWT
  token，缓存到本地并输出到 stdout，供其他 skill / 脚本 / Agent 复用。当其他 skill 报无权限/需要登录/缺少鉴权
  token，或用户说"登录一下 xxx 环境"、"拿一下 xxx 的 token"、"鉴权失败"、"401"、"jwt
  过期"时使用。调用方需要传入目标站点的完整 origin（如 https://cmes-fat.gz.cvte.cn）。
invocable: true
author: zhuzhiyong
group: mfg
tags:
  - 登录
  - 鉴权
  - login
version: 0.0.5
---

> **`SKILL_DIR`**：本 SKILL.md 所在目录的绝对路径（运行时通过 `Path(__file__).resolve().parent.parent` 自动推导，不要硬编码）。

# 制造登录鉴权

## 这个 skill 解决什么

当其他 skill / 脚本 / Agent 需要调用业务接口，但缺少有效的 JWT 鉴权 token（典型表现：401、`没有权限`、`token expired`），调用本 skill 即可：

1. 浏览器自动打开目标站点；用户在浏览器里完成登录（SSO / 账号密码 / 扫码均可）。
2. 用户回到终端按回车告知"我登录好了"。
3. 脚本复用浏览器里的 cookie 调 `GET <origin>/api/auth/getJwtByToken`，取出 JWT；同时从 cookie 中提取 UUID 格式的 auth token（`x-auth-token-*` 或 `*cmes*info` 类名称）。
4. 写入 `<SKILL_DIR>/.cache/<host>.json`，同时以 JSON 格式打印到 stdout。

## 何时调用

- 其他 skill 报：`401 Unauthorized` / `鉴权失败` / `token 过期` / `请先登录`。
- 用户说："登录一下 mes-uat" / "帮我拿 sit 的 token" / "更新一下鉴权"。
- 任何脚本/Agent 在请求业务接口前需要一个新鲜 JWT。

## 前置依赖

```bash
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # 或由调用方确定
cd "$SKILL_DIR"
pip install -r scripts/requirements.txt
python -m playwright install chromium    # 仅首次需要
```

> Python ≥ 3.9；脚本只依赖 `playwright` 和 `requests`。
> 如果当前环境有 venv，请使用 `$SKILL_DIR/.venv/bin/python` 来执行脚本。

## 用法

调用方需要提供一个 **origin**（协议 + host，不带 path）。例：

```bash
# SKILL_DIR 由调用方根据 skill 实际安装位置确定
python "$SKILL_DIR/scripts/login.py" https://cmes-fat.gz.cvte.cn --poll --force
```

参数：

| 参数                  | 必填 | 说明                                                                                                   |
| --------------------- | ---- | ------------------------------------------------------------------------------------------------------ |
| `<origin>` (位置参数) | 是   | 目标站点 origin，如 `https://cmes-fat.gz.cvte.cn`                                                      |
| `--force`             | 否   | 忽略缓存，强制重新走登录流程                                                                           |
| `--poll`              | 否   | 非交互模式：打开浏览器后每 3 秒轮询接口，登录成功自动完成（**Claude Code 等非 tty 环境必须加此参数**） |
| `--no-prompt`         | 否   | 命中缓存就直接输出；不命中且不能交互时直接报错退出（给纯脚本场景用）                                   |

> **在 Claude Code / Cursor 中调用时，务必加 `--poll`**（脚本也会自动检测 stdin 非 tty 时启用轮询）。

成功时：

- **stdout** 输出一行 JSON：

  ```json
  {
    "jwt": "eyJhbG...",
    "cookie_token": "uuid-value",
    "cookie_name": "x-auth-token-qms",
    "x-jwt-type": "1",
    "x-current-user-type": "user",
    "x-user-type-value": "some-value"
  }
  ```

  - `jwt`：JWT 格式 token，请求时放在 header `x-auth-token` 上。
  - `cookie_token`：UUID 格式 token（从浏览器 cookie 中提取），请求时作为 cookie 传递。
  - `cookie_name`：cookie 的字段名（`x-auth-token-*` 或 `*cmes*info` 类名称），按环境自动匹配。
  - `x-jwt-type`：（有值时才出现）请求时放在 header `x-jwt-type` 上。
  - `x-current-user-type`：（有值时才出现）请求时放在 header `x-current-user-type` 上。
  - `x-user-type-value`：（有值时才出现）请求时放在 header `x-user-type-value` 上。

- **stderr** 输出过程日志，不污染管道。
- **退出码** `0`。

失败时退出码非 0，stderr 写明原因（接口非 status=0、网络错误、用户取消等）。

## 缓存

- 路径：`<SKILL_DIR>/.cache/<host>.json`，按 host 分文件（`cmes-fat.gz.cvte.cn.json`）。
- 内容：`{"origin": "...", "jwt": "...", "cookie_token": "...", "cookie_name": "...", "exp": <unix秒>, "fetched_at": <unix秒>}`。
- 命中策略：缓存存在且距离 `exp` 还有 ≥ 60 秒时复用，否则重新登录。
- 浏览器持久化 profile 位于 `<SKILL_DIR>/.profile/`，下次再打开同一站点通常免登录。

> `.cache/` 与 `.profile/` 已通过本 skill 的 `.gitignore` 排除。

## 给其他 skill / Agent 的复用方式

### token 与 header 的用途

| 类型              | 字段                  | 请求时放置位置                                     | 格式        |
| ----------------- | --------------------- | -------------------------------------------------- | ----------- |
| JWT               | `jwt`                 | Header: `x-auth-token: <jwt>`                      | `eyJhbG...` |
| Cookie Token      | `cookie_token`        | Cookie: `<cookie_name>=<cookie_token>`             | UUID        |
| JWT Type          | `x-jwt-type`          | Header: `x-jwt-type: <value>`（有值才传）          | string      |
| Current User Type | `x-current-user-type` | Header: `x-current-user-type: <value>`（有值才传） | string      |
| User Type Value   | `x-user-type-value`   | Header: `x-user-type-value: <value>`（有值才传）   | string      |

### Bash 示例

```bash
# SKILL_DIR 需由调用方根据实际安装路径确定
RESULT=$(python "$SKILL_DIR/scripts/login.py" "$ORIGIN") || exit 1
JWT=$(echo "$RESULT" | python -c "import sys,json; print(json.load(sys.stdin)['jwt'])")
COOKIE_TOKEN=$(echo "$RESULT" | python -c "import sys,json; d=json.load(sys.stdin); print(d['cookie_name']+'='+d['cookie_token'])")

# 构建 header（有值才传）
HEADERS="-H \"x-auth-token: $JWT\""
for KEY in x-jwt-type x-current-user-type x-user-type-value; do
  VAL=$(echo "$RESULT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('$KEY',''))")
  [ -n "$VAL" ] && HEADERS="$HEADERS -H \"$KEY: $VAL\""
done

curl -H "x-auth-token: $JWT" "$ORIGIN/api/xxx/yyy"
```

### Python 示例（直接读缓存）

```python
import json, time, subprocess, pathlib

def get_skill_dir() -> pathlib.Path:
    """调用方需自行确定 auto-login skill 的安装路径。"""
    import os
    return pathlib.Path(os.environ.get("AUTO_LOGIN_SKILL_DIR", ""))

def get_tokens(origin: str) -> dict:
    """返回 {"jwt": "...", "cookie_token": "...", "cookie_name": "...", "x-jwt-type": ..., "x-current-user-type": ..., "x-user-type-value": ...}（后三个有值才存在）"""
    skill_dir = get_skill_dir()
    host = origin.split("//", 1)[1].split("/", 1)[0]
    cache = skill_dir / ".cache" / f"{host}.json"
    if cache.exists():
        data = json.loads(cache.read_text())
        if data.get("exp", 0) - time.time() > 60:
            return {"jwt": data["jwt"], "cookie_token": data.get("cookie_token", ""), "cookie_name": data.get("cookie_name", "")}
    raw = subprocess.check_output(
        ["python", str(skill_dir / "scripts" / "login.py"), origin], text=True
    ).strip()
    return json.loads(raw)
```

## 交互流程（用户视角）

1. 终端打印：`[auto-login] 正在打开 https://xxx ，请在浏览器中完成登录…`
2. 弹出 Chromium 窗口，跳转到 origin。
3. 用户登录完成后回到终端，按回车。
4. 终端打印 `[auto-login] 调用 /api/auth/getJwtByToken …`，随后打印一行 token，浏览器自动关闭。

如果 60 秒内用户没有按回车，脚本会再次提示；持续无响应则 10 分钟后超时退出。

## 接口约定

- 方法：`GET`
- URL：`<origin>/api/auth/getJwtByToken`
- 鉴权：浏览器登录后的 cookie（脚本先从 playwright context 取出 cookie，优先用 `requests` 调接口；若 SSL 握手失败则自动回退到 `http.client`）。
- 成功响应形如：
  ```json
  { "data": { "status": "0", "data": { "token": "eyJhbGciOiJIUzI1NiJ9..." } } }
  ```
- 取 token 路径：`response.json()["data"]["data"]["token"]`。如未来后端调整字段，修改 `scripts/login.py` 的 `extract_token()`。

## 故障排查

| 现象                  | 处理                                                                              |
| --------------------- | --------------------------------------------------------------------------------- |
| 浏览器没弹出          | 确认已执行 `python -m playwright install chromium`                                |
| `status != 0`         | 登录态拿到了但接口拒发；让用户在浏览器里手动访问 `/api/auth/getJwtByToken` 看响应 |
| 一直 401              | profile 里 cookie 过期；删 `<SKILL_DIR>/.profile/` 重来，或加 `--force`           |
| 拿到的 token 立即过期 | 解码 JWT 看 `exp`，通常是后端时钟问题，联系后端                                   |
| SSL 握手失败          | 脚本会自动回退到 `http.client`；如仍失败，检查网络是否可达                        |
