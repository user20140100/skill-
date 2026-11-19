---
name: portal-sso
description: >-
  对接 CVTE 门户单点登录（SSO）。支持 CAS 模式和 OAuth 2.0 authorization_code 模式。当用户提到门户对接、SSO
  对接、单点登录、CAS 对接、OAuth 对接、portal 登录、ticket 校验、门户登录跳转时使用。
version: 1.0.0
author: huangweihong
---

# 门户 SSO 对接

帮助业务系统对接 CVTE 门户单点登录，支持 **CAS 模式** 和 **OAuth 2.0 模式**。

## ⚠️ AI 对接前必须先询问用户

在编写任何代码之前，**必须先向用户确认以下问题**（使用 AskQuestion 工具询问）：

### 问题 1：对接环境

询问用户要对接的是**测试环境**还是**正式环境**，并根据选择提醒注意事项：

**测试环境（fat / uat）**：

- 门户地址：`op-fat.cvte.com`
- ~~注册业务系统由 skill 自动发起接口请求，无需用户手动联系人员~~（自动提单功能已暂停，请用户手动在 ITSM 提单注册业务系统）
- 域名校验**不生效**，本地开发可直接用 `localhost` 作为回调地址
- fat 和 uat 共用同一套门户测试环境

**正式环境（生产）**：

- 门户地址：`home.cvte.com`
- ~~注册业务系统由 skill 自动发起接口请求，无需用户在 ITSM 手动提单~~（自动提单功能已暂停，请用户手动在 ITSM 提单注册业务系统）
- 域名校验**生效**，回调地址的域名必须与门户中注册的域名一致，否则会报 `4000004` 错误
- 上线前务必确认门户管理员已为业务系统绑定了正确的域名

### 问题 2：对接模式

询问用户选择 **CAS 模式** 还是 **OAuth 2.0 模式**：

- **CAS 模式**：流程较简单，一次 ticket 校验即可拿到用户信息 + jwt，适合内部快速对接。但需要额外申请 **IAC 凭证**（用于 ticket 校验请求头的 `x-iac-token`）
- **OAuth 2.0 模式**：标准 authorization_code 流程，需要多次请求（获取 code → 换 access_token → 获取用户信息），适合需要标准 OAuth 协议的场景。不需要 IAC 凭证

### 问题 3：项目类型

仅当用户需要生成 SSO 对接代码时询问项目类型。若当前目标仅是申请 `appId` / `client_id`，跳过该问题。

询问用户的项目是**全栈项目**还是**前后端分离项目**：

- **全栈项目**（前后端在同一 Node.js 项目中，如 Koa / Express + 前端）：同时生成前端跳转代码和 Node.js 服务端校验代码
- **前后端分离项目**（前端 SPA + 后端独立服务，分别由不同团队或不同技术栈开发）：分别生成前端代码和后端接口实现代码，后端语言可选

### 提示用户申请 appId

当用户出现以下表达时，提示用户需要手动在 ITSM 提单完成注册：

- 申请 `appId`
- 申请 `client_id`
- 注册业务系统
- 发起门户注册
- 开通门户 SSO

在确认对接模式后，AI 应**主动询问用户是否已获取 `appId`（CAS 模式）或 `client_id`（OAuth 2.0 模式）**。如果用户尚未获取，AI 应**提示用户手动在 ITSM 提单完成业务系统注册申请**（自动提单功能已暂停）：

<!-- **自动申请流程（已暂停）**：

- 按 `doc/itsm.md` 组装提单参数，并使用 `scripts/create_itsm_issue.sh` 执行流程
- `reporter.name` 从 `cskills who` 自动获取
- `summary` 和 `description` 由用户提供后写入请求体
- ITSM 凭证默认通过 `create_itsm_issue_from_apollo` 自动从 Apollo 拉取（也支持显式注入环境变量覆盖）
- 自动申请流程中不需要询问项目类型 -->

<!-- 以下提单模板已暂停使用
向用户收集 `summary` 和 `description` 时，必须提供以下模板：

- `summary` 模板：`申请标题，如门户申请appId`
- `description` 模板：
  1. 应用类型：可选值为 公共、研发、商务、供应链、其他
  2. 应用名称：如 ZPB
  3. 应用描述：如 校园招聘管理系统
  4. 应用访问地址：从应用列表点击后跳转的地址，如果采用方式一，则需要提供 SSO 初始化接口的地址，否则直接提供应用访问地址
  5. 可见范围：全员、或者某个组织架构、或者某些员工，根据实际需要提供

注册时需提供以下信息：应用类型、应用名称、应用描述、应用访问地址、可见范围。
-->

**如果用户选择了 CAS 模式**，还需额外提示用户申请 **IAC 凭证**（`appId` 和 `appSecret`，用于获取 `x-iac-token`）：

- IAC 申请地址：[https://iac.gz.cvte.cn/pages/login](https://iac.gz.cvte.cn/pages/login)，使用域账号**自主登录注册**，创建应用即可获取 `appId` 和 `appSecret`，无需找他人审批
- **IAC 只有一个环境**，测试和生产共用同一套 IAC 系统
- IAC 的 `appId` / `appSecret` 与门户派发的 `appId` 是**完全不同的两套凭证**：IAC 凭证在 IAC 系统自助申请，门户 `appId` 在门户系统注册业务应用时获取，两者不可混淆

如果用户尚未准备好这些凭证，应建议用户先完成申请再继续对接。

### 代码对接完成后的必答说明

在完成 SSO 代码对接并给出代码后，AI 必须主动补充以下“凭证申请与用途说明”（即使用户未追问，也要说明），并使用面向业务用户的专业表述，不暴露脚本路径或实现细节：

1. **接口授权中心（IAC）应用凭证申请说明**
   - 申请入口：`https://iac.gz.cvte.cn/pages/login`
   - 使用域账号登录后，在 IAC 平台创建应用，获取 `appId` 与 `appSecret`
   - 凭证用途：用于获取 `x-iac-token`，并在 CAS 模式下调用 `ticket_validate` 接口进行身份校验

2. **门户业务应用标识（`appId` / `client_id`）申请说明**
   - 需用户在 ITSM 手动提单完成业务系统注册（自动提单功能已暂停）
   - 门户标识用于门户身份映射与回调流程，对应 SSO 对接中的业务系统标识

3. **凭证边界说明（必须强调）**
   - IAC 的 `appId` / `appSecret` 与门户的 `appId` / `client_id` 属于两套独立凭证体系
   - 两类凭证用途不同、签发系统不同，禁止混用

确认后，根据用户选择的环境设置对应的 `host`，只实现对应模式的代码，并根据项目类型决定生成全栈代码还是前后端分离代码。

**前后端分离项目额外要求**：AI 需要先检查用户项目的前端技术栈（React/Vue、路由库、构建工具 Vite/webpack 等），根据实际框架生成对应风格的代码。下方示例以 React 为主，AI 应根据实际项目框架做适配。

### 问题 4：后端技术栈（仅前后端分离项目需要）

当用户在问题 3 中选择**前后端分离项目**后，使用 AskQuestion **追问后端技术栈**，以便为后端生成可直接使用的接口实现代码：

- **Java（Spring Boot）**
- **Python（Flask）**
- **Python（FastAPI）**
- **Go（Gin）**
- **Node.js（Koa）**
- **Node.js（Express）**
- **其他**（用户自行输入框架名称）

AI 根据用户选择的语言和框架，生成该语言惯用风格的后端接口实现代码。如果用户选择"其他"，让用户补充具体语言和框架名称后再生成。

---

## 前置准备

在对接之前，需要完成以下两步：

### 1. 注册业务系统

在 ITSM 手动提单完成业务系统注册，获取门户派发的 `appId`（CAS 模式）或 `client_id`（OAuth 2.0 模式）。注册所需信息：应用类型、应用名称、应用描述、应用访问地址、可见范围。

### 2. 获取 iacToken（CAS 模式必需）

CAS 模式的 ticket 校验接口需要在请求头中携带 `x-iac-token`，该 token 通过**接口授权中心（IAC）**获取。

**申请 IAC 凭证**：访问 [https://iac.gz.cvte.cn/pages/login](https://iac.gz.cvte.cn/pages/login)，使用域账号**自主登录注册**，创建应用即可获取 IAC 的 `appId` 和 `appSecret`，无需找他人审批。IAC 只有一个环境，测试和生产共用。

> ⚠️ **注意**：此处的 IAC `appId` / `appSecret` 是在 IAC 系统中**自主申请**的，与门户注册业务系统时获取的 `appId` 是**两套完全不同的凭证**，不可混淆。

**获取 accessToken 接口**：

```
GET https://itapis.cvte.com/iac/app/access_token?appid={appId}&secret={appSecret}
```

返回示例：

```json
{
  "status": 200,
  "errCode": 0,
  "data": {
    "accessToken": "418fba21-9f7b-483a-b267-9ad4701cd4c9",
    "accessTokenExpire": 1484555205178
  }
}
```

服务端示例（Node.js）：

```typescript
let cachedIacToken: string | null = null;

async function getIacToken(appId: string, appSecret: string): Promise<string> {
  const response = await fetch(`https://itapis.cvte.com/iac/app/access_token?appid=${appId}&secret=${appSecret}`);
  const result = await response.json();
  if (result.errCode !== 0) {
    throw new Error(`获取 iacToken 失败: ${result.errMsg}`);
  }
  cachedIacToken = result.data.accessToken;
  return cachedIacToken;
}
```

**注意事项**：

- `accessToken` 有效期为 **2 小时**，建议每小时刷新一次并缓存
- 请求时若 token 未过期会自动续期，过期则生成全新 token
- 此处的 IAC `appId` / `appSecret` 与门户派发的 `appId` 是**不同的**，分别在 IAC 和门户两个系统中获取

**IAC 错误码**：

| 错误码            | 含义                  |
| ----------------- | --------------------- |
| 40101             | 该 app 不存在         |
| 40102             | 该 system 不存在      |
| 40103             | 该 app 权限不足       |
| 40104             | 该 token 过期或不存在 |
| 40002             | 访问频率频繁          |
| 50001/50002/50003 | 系统内部错误          |

## 环境地址

| 环境                   | Host              |
| ---------------------- | ----------------- |
| 测试（fat/uat 均使用） | `op-fat.cvte.com` |
| 生产                   | `home.cvte.com`   |

---

## CAS 模式对接

### 流程概览

1. 检测 cookie/会话过期 → 重定向至门户登录
2. 门户登录成功 → 重定向回业务系统，携带 `ticket`（有效期 120 秒）
3. 业务系统用 `ticket` + `appId` 调用 ticket 校验接口 → 获取用户信息和 jwt
4. 业务系统设置 cookie，保存会话

### Step 1: 构造重定向地址

当检测到用户会话过期时，跳转到以下地址：

```
https://{host}/login?redirect=encodeURIComponent("/portal/app_oauth?appId={appId}&redirect=" + encodeURIComponent(业务系统回调地址) + "&type=op")
```

**关键点**：

- `redirect` 参数需要对内部地址做 `encodeURIComponent` 编码
- 业务系统回调地址也需要编码
- 嵌套参数需要做多层编码

前端示例：

```typescript
function redirectToPortalLogin(host: string, appId: string, callbackUrl: string) {
  const innerRedirect = `/portal/app_oauth?appId=${appId}&redirect=${encodeURIComponent(callbackUrl)}&type=op`;
  const loginUrl = `https://${host}/login?redirect=${encodeURIComponent(innerRedirect)}`;
  window.location.href = loginUrl;
}
```

### Step 2: 接收 ticket

门户登录成功后，会重定向到业务系统回调地址，URL 上携带 `ticket` 参数：

```
https://业务系统地址?ticket=xxxxxxxxxx
```

### Step 3: 校验 ticket（服务端）

**请求方式**：`GET https://{host}/apis/v1/ticket_validate`

| 参数名      | 位置   | 含义                                             |
| ----------- | ------ | ------------------------------------------------ |
| x-iac-token | header | 通过 IAC 获取的 accessToken（见前置准备第 2 步） |
| appId       | query  | 门户派发的系统标识                               |
| ticket      | query  | 门户生成的身份凭证                               |

服务端示例（Node.js）：

```typescript
async function validateTicket(host: string, appId: string, ticket: string, iacToken: string) {
  const response = await fetch(`https://${host}/apis/v1/ticket_validate?appId=${appId}&ticket=${ticket}`, {
    headers: { "x-iac-token": iacToken },
  });
  const result = await response.json();
  if (result.status !== "0") {
    throw new Error(`Ticket 校验失败: ${result.message} (${result.status})`);
  }
  return result.data; // { user: {...}, jwt: "..." }
}
```

> **提示**：`iacToken` 通过 IAC 的 `GET https://itapis.cvte.com/iac/app/access_token` 接口获取，需提前申请 IAC 的 `appId` 和 `appSecret`，详见前置准备。

返回成功示例：

```json
{
  "status": "0",
  "data": {
    "user": {
      "id": "xxx",
      "account": "zhangsan",
      "name": "张三",
      "telephone": "13800138000",
      "email": "zhangsan@cvte.com",
      "gender": "1",
      "accountType": "2"
    },
    "jwt": "eyJhbGciOiJSUzI1NiJ9..."
  }
}
```

**错误码**：

| status  | 含义                     |
| ------- | ------------------------ |
| 4000000 | IAC 校验失败             |
| 4000001 | appId 和 ticket 必须提供 |
| 4000002 | ticket 无效或已过期      |
| 4000003 | appId 与 ticket 不匹配   |
| 5000001 | ticket 校验出错          |
| 5000002 | 获取用户信息失败         |
| 5000003 | 获取 jwt 失败            |

### Step 4: 设置会话

获取到用户信息和 jwt 后，业务系统自行设置 cookie 保存会话。jwt 可调用 jwt 服务刷新接口进行续期。

### CAS 登出

`GET https://{host}/portal/logout`

| 参数名   | 位置  | 含义                              |
| -------- | ----- | --------------------------------- |
| appId    | query | 门户派发的系统标识                |
| redirect | query | 登出后重定向地址（需两层 encode） |

### CAS 前后端分离项目对接

适用于前后端分离项目，前端为 React、Vue 等 SPA，后端为独立服务。以下前端示例以 React 为主，AI 应根据用户实际框架做适配。

#### 1. Auth 工具模块

创建 `src/utils/auth.ts`（或项目约定的工具目录）：

```typescript
const PORTAL_HOST = "op-fat.cvte.com"; // 或 home.cvte.com
const APP_ID = "门户派发的appId";

export function redirectToPortalLogin() {
  const callbackUrl = window.location.origin + "/auth/callback";
  const innerRedirect = `/portal/app_oauth?appId=${APP_ID}&redirect=${encodeURIComponent(callbackUrl)}&type=op`;
  window.location.href = `https://${PORTAL_HOST}/login?redirect=${encodeURIComponent(innerRedirect)}`;
}

export async function loginWithTicket(ticket: string) {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticket }),
  });
  if (!res.ok) throw new Error("登录失败");
  return res.json();
}

export async function getUser() {
  const res = await fetch("/api/user");
  if (!res.ok) return null;
  const data = await res.json();
  return data.user;
}

export async function logout() {
  await fetch("/api/auth/logout", { method: "POST" }).catch(() => {});
  const redirect = encodeURIComponent(window.location.origin);
  window.location.href = `https://${PORTAL_HOST}/portal/logout?appId=${APP_ID}&redirect=${redirect}`;
}
```

#### 2. 回调页组件

创建回调路由对应的页面组件（如 `src/pages/AuthCallback.tsx`），注册到路由 `/auth/callback`：

```tsx
import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { loginWithTicket } from "@/utils/auth";

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const ticket = searchParams.get("ticket");
    if (!ticket) return;
    loginWithTicket(ticket)
      .then(() => navigate("/", { replace: true }))
      .catch(() => navigate("/login", { replace: true }));
  }, []);

  return <div>登录中...</div>;
}
```

#### 3. 路由守卫 / 登录态检测

在应用入口或路由守卫中调用 `getUser()`，未登录时跳转门户：

```tsx
import { getUser, redirectToPortalLogin } from "@/utils/auth";

// 在根组件 useEffect 或路由守卫中
const user = await getUser();
if (!user) {
  redirectToPortalLogin();
  return;
}
```

#### 4. Dev Server 代理配置

开发时需要把 `/api` 请求代理到后端服务地址：

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://后端服务地址",
        changeOrigin: true,
      },
    },
  },
});
```

> webpack 项目在 `devServer.proxy` 中配置，格式相同。

#### 5. 后端接口实现代码

根据用户在问题 4 中选择的后端技术栈，生成以下三个接口的**完整可运行代码**。代码应使用目标语言/框架的惯用风格，包含路由注册、请求处理、错误处理。

需要实现的接口：

| 接口               | 方法 | 请求体                | 返回                         | 核心逻辑                                                                                                                                                                        |
| ------------------ | ---- | --------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/auth/login`  | POST | `{ "ticket": "xxx" }` | `{ "user": { ... } }`        | 调用门户 `GET https://{host}/apis/v1/ticket_validate?appId={appId}&ticket={ticket}`（header 携带 `x-iac-token`），校验成功后创建会话，返回用户信息。门户接口详见上方 CAS Step 3 |
| `/api/user`        | GET  | 无                    | `{ "user": { ... } }` 或 401 | 返回当前会话用户信息，未登录返回 401                                                                                                                                            |
| `/api/auth/logout` | POST | 无                    | 200                          | 清除服务端会话                                                                                                                                                                  |

生成的代码**必须包含**：

- **IAC token 获取与缓存**：调用 `GET https://itapis.cvte.com/iac/app/access_token?appid={appId}&secret={appSecret}` 获取 token，有效期 2 小时，需定时刷新并缓存（详见前置准备第 2 步）
- **会话管理**：使用目标框架的 session 机制（如 Java 的 HttpSession、Python 的 flask-session 等）
- **错误处理**：门户返回错误时，将错误信息透传给前端
- **配置项外置**：`appId`、IAC `appId`/`appSecret`、`portalHost` 等作为配置项，不硬编码

---

## OAuth 2.0 模式对接

### 流程概览

1. 业务系统通过 cookie 校验用户会话是否过期，若过期，跳转至门户提供的获取 authorization code 接口
2. 用户在门户登录授权后，若具有访问该业务系统的权限，门户重定向至上一步提供的重定向地址，携带 `code`
3. 业务系统获取到 `code`，请求门户的 access_token 接口换取 `access_token`（服务端）
4. 业务系统获取到 `access_token`，请求门户的用户信息接口获取用户信息，根据用户信息完成业务登录（服务端）

### Step 1: 获取 authorization code

重定向用户至门户授权页面：

`GET https://{host}/portal/oauth2/authorize`

| 参数名        | 位置  | 必选 | 含义                              |
| ------------- | ----- | ---- | --------------------------------- |
| client_id     | query | 是   | 门户派发的系统标识                |
| redirect_uri  | query | 是   | 授权后重定向地址（需两层 encode） |
| response_type | query | 是   | 固定为 `code`                     |
| scope         | query | 否   | 申请权限范围（目前无实际作用）    |
| state         | query | 否   | 客户端状态值，门户会原样返回      |

前端示例：

```typescript
function redirectToOAuthAuthorize(host: string, clientId: string, callbackUrl: string, state?: string) {
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: callbackUrl,
    response_type: "code",
  });
  if (state) params.set("state", state);
  window.location.href = `https://${host}/portal/oauth2/authorize?${params.toString()}`;
}
```

**redirect_uri 编码规则**：`URLSearchParams` 会自动对值做 URL 编码，**不要**再手动 `encodeURIComponent`，否则会双重编码导致门户把 redirect_uri 当成相对路径。如果回调地址自身携带 query 参数（如 `http://xx.cvte.com/oauth?next=/home?role=1`），需先对内层参数 encode 后再拼接回调地址：`http://xx.cvte.com/oauth?next=${encodeURIComponent('/home?role=1')}`，然后直接传给 `URLSearchParams`。

**错误码**：

| status  | 含义                              |
| ------- | --------------------------------- |
| 4000001 | client_id 必须提供                |
| 4000002 | 该用户没有权限                    |
| 4000003 | app 不存在                        |
| 4000004 | 当前业务域名没有使用该 app 的权限 |
| 5000001 | 获取用户信息失败                  |
| 5000002 | 生成凭证失败                      |

### Step 2: 接收 authorization code

授权成功后，门户重定向到 `redirect_uri`，URL 上携带 `code` 参数。

### Step 3: 获取 access_token（服务端）

**请求方式**：`POST https://{host}/portal/oauth2/token`

| 参数名       | 位置 | 含义                               |
| ------------ | ---- | ---------------------------------- |
| grant_type   | body | 固定为 `authorization_code`        |
| code         | body | 上一步获取的 code（有效期 120 秒） |
| redirect_uri | body | 必须与 Step 1 中传的一致           |

服务端示例（Node.js）：

```typescript
async function getAccessToken(host: string, code: string, redirectUri: string) {
  const response = await fetch(`https://${host}/portal/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grant_type: "authorization_code",
      code,
      redirect_uri: redirectUri,
    }),
  });
  const result = await response.json();
  if (result.status) {
    throw new Error(`获取 access_token 失败: ${result.message} (${result.status})`);
  }
  return result; // { access_token: "xxx", expires_in: 120 }
}
```

返回示例：

```json
{
  "access_token": "ebc93dfb-fab1-4294-b96d-91d015093428",
  "expires_in": 120
}
```

**错误码**：

| status  | 含义               |
| ------- | ------------------ |
| 4000001 | 重定向地址校验失败 |
| 4000003 | code 必须提供      |
| 4000004 | code 无效或已过期  |
| 5000001 | code 校验出错      |

### Step 4: 获取用户信息（服务端）

**请求方式**：`GET https://{host}/portal/oauth2/user`

| 参数名        | 位置   | 含义                                                                          |
| ------------- | ------ | ----------------------------------------------------------------------------- |
| authorization | header | 组装格式：`"Bearer xxx"`，其中 xxx 为上一步获取的 access_token，过期时间 120S |

服务端示例（Node.js）：

```typescript
async function getUserInfo(host: string, accessToken: string) {
  const response = await fetch(`https://${host}/portal/oauth2/user`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const result = await response.json();
  if (result.status) {
    throw new Error(`获取用户信息失败: ${result.message} (${result.status})`);
  }
  return result; // { id, account, name, email, telephone, gender, accountType, ... }
}
```

返回示例：

```json
{
  "username": "xxxxx",
  "id": "99a16d1c8afd4b8d8dd5f1aabb86e062",
  "account": "xxxxx",
  "name": "xxxx",
  "telephone": "xxxxx",
  "email": "huangweihong@cvte.com",
  "gender": "1",
  "accountType": "2",
  "simUid": "00005452"
}
```

**错误码**：

| status  | 含义             |
| ------- | ---------------- |
| 5000000 | 获取用户信息失败 |
| 5000002 | 获取用户信息失败 |

### Step 5: 设置会话

根据获取到的用户信息，业务系统自行设置 cookie 保存会话。

### OAuth 2.0 登出

`GET https://{host}/portal/oauth2/logout`

| 参数名   | 位置  | 含义                              |
| -------- | ----- | --------------------------------- |
| redirect | query | 登出后重定向地址（需两层 encode） |

### OAuth 2.0 前后端分离项目对接

适用于前后端分离项目，前端为 React、Vue 等 SPA，后端为独立服务。以下前端示例以 React 为主，AI 应根据用户实际框架做适配。

#### 1. Auth 工具模块

创建 `src/utils/auth.ts`（或项目约定的工具目录）：

```typescript
const PORTAL_HOST = "op-fat.cvte.com"; // 或 home.cvte.com
const CLIENT_ID = "门户派发的client_id";

export function redirectToPortal() {
  const callbackUrl = window.location.origin + "/oauth/callback";
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    redirect_uri: callbackUrl,
    response_type: "code",
  });
  window.location.href = `https://${PORTAL_HOST}/portal/oauth2/authorize?${params.toString()}`;
}

export async function loginWithCode(code: string) {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) throw new Error("登录失败");
  return res.json();
}

export async function getUser() {
  const res = await fetch("/api/user");
  if (!res.ok) return null;
  const data = await res.json();
  return data.user;
}

export async function logout() {
  await fetch("/api/auth/logout", { method: "POST" }).catch(() => {});
  const redirect = encodeURIComponent(window.location.origin);
  window.location.href = `https://${PORTAL_HOST}/portal/oauth2/logout?redirect=${redirect}`;
}
```

#### 2. 回调页组件

创建回调路由对应的页面组件（如 `src/pages/OAuthCallback.tsx`），注册到路由 `/oauth/callback`：

```tsx
import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { loginWithCode } from "@/utils/auth";

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) return;
    loginWithCode(code)
      .then(() => navigate("/", { replace: true }))
      .catch(() => navigate("/login", { replace: true }));
  }, []);

  return <div>登录中...</div>;
}
```

#### 3. 路由守卫 / 登录态检测

在应用入口或路由守卫中调用 `getUser()`，未登录时跳转门户：

```tsx
import { getUser, redirectToPortal } from "@/utils/auth";

// 在根组件 useEffect 或路由守卫中
const user = await getUser();
if (!user) {
  redirectToPortal();
  return;
}
```

#### 4. Dev Server 代理配置

开发时需要把 `/api` 请求代理到后端服务地址：

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://后端服务地址",
        changeOrigin: true,
      },
    },
  },
});
```

> webpack 项目在 `devServer.proxy` 中配置，格式相同。

#### 5. 后端接口实现代码

根据用户在问题 4 中选择的后端技术栈，生成以下三个接口的**完整可运行代码**。代码应使用目标语言/框架的惯用风格，包含路由注册、请求处理、错误处理。

需要实现的接口：

| 接口               | 方法 | 请求体              | 返回                         | 核心逻辑                                                                                                                                                                                                                                                                                                                        |
| ------------------ | ---- | ------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/auth/login`  | POST | `{ "code": "xxx" }` | `{ "user": { ... } }`        | 1) 调用门户 `POST https://{host}/portal/oauth2/token`（body: `{ grant_type: "authorization_code", code, redirect_uri }`）换取 access_token；2) 调用门户 `GET https://{host}/portal/oauth2/user`（header: `Authorization: Bearer {access_token}`）获取用户信息；3) 创建会话，返回用户信息。门户接口详见上方 OAuth Step 3、Step 4 |
| `/api/user`        | GET  | 无                  | `{ "user": { ... } }` 或 401 | 返回当前会话用户信息，未登录返回 401                                                                                                                                                                                                                                                                                            |
| `/api/auth/logout` | POST | 无                  | 200                          | 清除服务端会话                                                                                                                                                                                                                                                                                                                  |

生成的代码**必须包含**：

- **两步门户调用**：先用 code 换 access_token，再用 access_token 获取用户信息，任一步失败需返回明确错误
- **会话管理**：使用目标框架的 session 机制（如 Java 的 HttpSession、Python 的 flask-session 等）
- **错误处理**：门户返回错误时，将错误信息透传给前端
- **配置项外置**：`client_id`、`portalHost`、`redirect_uri` 等作为配置项，不硬编码

---

## 常见问题排查

| 错误码           | 含义                      | 解决方式                                                   |
| ---------------- | ------------------------- | ---------------------------------------------------------- |
| 4000002（CAS）   | 角色未授权                | 联系门户管理员授权                                         |
| 4000004（CAS）   | 域名和 appId 未绑定       | 联系门户管理员绑定域名                                     |
| 4000002（OAuth） | 用户没有权限              | 联系门户管理员分配权限                                     |
| 4000004（OAuth） | 域名没有使用该 app 的权限 | 联系门户管理员绑定域名（生产环境校验域名，测试环境不校验） |

## 详细文档

- CAS 模式完整文档：[doc/cas.md](doc/cas.md)
- OAuth 2.0 模式完整文档：[doc/oauth2.0.md](doc/oauth2.0.md)
- IAC Token 获取文档：[doc/iacToken.md](doc/iacToken.md)
- 准备工作与注册流程：[doc/remark.md](doc/remark.md)
