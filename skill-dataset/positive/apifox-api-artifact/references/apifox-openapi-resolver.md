# Apifox Open API Resolver

当用户提供 Apifox 协作链接（例如 `http://kdl-apifox.test.seewo.com/link/project/345082/apis/api-3471450`）时，优先使用这个 resolver。

## 目标

把协作链接中的 `projectId` 和 `apiId` 转换成单个接口的结构化数据，避免依赖当前 Apifox MCP 对协作链接的解析能力。

## 非协商规则

> [!CRITICAL]
> 不要把 Apifox 访问令牌写入仓库、skill 文件、Mockoon 文件或生成的 TypeScript 文件。

-   不要编造接口结构。
-   不要把协作链接域名当成 Open API base URL。
-   如果 resolver 无法返回结构化接口数据，必须明确进入 MCP 回退或替代输入流程。

## 配置

resolver 脚本位置：

`scripts/resolve-apifox-api.mjs`

认证来源：

-   优先使用 `APIFOX_ACCESS_TOKEN` 环境变量。
-   如果环境变量不存在，脚本会尝试读取 Cursor MCP 配置中的 `APIFOX_ACCESS_TOKEN`。
-   访问令牌使用 `Authorization: Bearer <token>` 调用开放 API。

可选环境变量：

-   `APIFOX_API_BASE_URL`：Apifox Open API 地址。未设置时优先读取 Cursor MCP 配置中的 `--apifox-api-base-url`，仍不存在则默认 `https://api.apifox.com`。
-   `APIFOX_ENDPOINTS_VERSION`：`GET /projects/{projectId}/http-endpoints` 的版本头，默认 `beta-2025-09-10`。
-   `APIFOX_EXPORT_VERSION`：`POST /v1/projects/{projectId}/export-openapi` 的版本头，默认 `2024-03-28`。

## 使用方式

> [!CRITICAL]
> 这是一个**只读脚本**（仅从 Apifox Open API 拉取数据，不修改本地文件），**必须直接执行，禁止向用户询问"是否执行"**。无论是单接口还是批量模式，都直接运行。只有在脚本执行失败时才向用户报告错误。

### 单接口

```sh
node .claude/skills/apifox-api-artifact/scripts/resolve-apifox-api.mjs "http://kdl-apifox.test.seewo.com/link/project/345082/apis/api-3471450"
```

输出：一个 JSON 对象。

### 批量接口（推荐）

```sh
node .claude/skills/apifox-api-artifact/scripts/resolve-apifox-api.mjs \
  "http://kdl-apifox.test.seewo.com/link/project/345082/apis/api-3471450" \
  "http://kdl-apifox.test.seewo.com/link/project/345082/apis/api-3471451" \
  "http://kdl-apifox.test.seewo.com/link/project/345082/apis/api-3471452"
```

输出：一个 JSON 数组，每项对应一个接口结果（成功为结构化数据，失败为 `{ error, detail }`）。

**批量优势**：同一 `projectId` 下的所有接口只调用一次 `GET /projects/{projectId}/http-endpoints`，而不是每个接口重复调用。10 个同项目接口 = 1 次 HTTP 请求（而非 10 次）。

如果 Cursor MCP 配置中已经包含 `APIFOX_ACCESS_TOKEN` 和 `--apifox-api-base-url`，无需设置环境变量即可运行。

成功时，stdout 输出一份结构化 JSON，至少包含：

-   `name`
-   `method`
-   `path`
-   `request_schema`
-   `response_schema`
-   `response_example`
-   `response_status_code`

stderr 可能包含 fallback warning，不要把 warning 当作接口结构。

## 解析流程

1. 从协作链接解析：
    -   `projectId`
    -   `apiId`
2. 首选调用：
    -   `GET /projects/{projectId}/http-endpoints`
    -   Header: `Authorization: Bearer <token>`
    -   Header: `X-Apidog-Api-Version: beta-2025-09-10`
    -   从 `data` 列表里按 `id === apiId` 找单接口。
3. 如果列表接口不可用或找不到接口，回退调用：
    -   `POST /v1/projects/{projectId}/export-openapi`
    -   Header: `Authorization: Bearer <token>`
    -   Header: `X-Apifox-Api-Version: 2024-03-28`
    -   Body 使用 `scope.type = SELECTED_ENDPOINTS` 和 `selectedEndpointIds: [apiId]`。
4. 将 Apifox endpoint 或导出的 OpenAPI 文档归一化为同一种结构化 JSON。

## 结果处理

如果 resolver 成功：

-   使用 resolver 输出作为阶段 2 的结构化接口数据。
-   继续按 TypeScript 与 Mockoon 输出流程生成文件。
-   最终总结中注明数据来源为 `apifox-openapi:http-endpoints` 或 `apifox-openapi:export-openapi`。

如果 resolver 失败：

-   缺少 `APIFOX_ACCESS_TOKEN`：提示用户设置本机环境变量，不要要求用户把 token 粘贴进代码。
-   401 / 403：提示 token 无效或账号没有项目权限。
-   404 / 找不到接口：提示协作链接里的接口可能不在当前账号可见范围，或 Open API base URL 不匹配。
-   网络错误：提示检查 `APIFOX_API_BASE_URL`，企业版可能需要专用开放 API 地址。
-   然后进入 `apifox-mcp.md` 的 MCP 读取流程；MCP 仍失败时再进入替代输入。

## 业务错误码提取

从 resolver 返回的 `description` 或 `x-apifox-description` 字段中，使用正则 `/^bizCode_(\d+)\s*=\s*(.+)$/gm` 提取业务错误码，传递给阶段 4。未提取到则跳过。
