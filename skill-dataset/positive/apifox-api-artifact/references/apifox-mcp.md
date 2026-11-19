# Apifox MCP

只有在需要确认 Apifox MCP 是否可用、检查配置位置、引导用户启动，或决定是否进入替代输入时，才使用这个参考文件。

## 目标

把一个 Apifox 接口链接转换成一份小而稳定的结构化数据，同时驱动 TypeScript 和 Mockoon 产物生成。

如果用户提供的是 Apifox 协作链接（`/link/project/<projectId>/apis/api-<apiId>`），先使用 `apifox-openapi-resolver.md`。只有 resolver 不可用、用户没有配置 Open API token、或 resolver 未能返回结构化数据时，才进入本文的 MCP 流程。

先判断当前会话里是否已经有可用的 Apifox MCP；只有在 MCP 没有运行时，才继续检查是否已经配置。

当前只支持以下两类宿主的配置检查：

- `Cursor`
- `VS Code`

## 非协商规则

> [!CRITICAL]
> 在任何阶段都不要伪造接口数据。

- 不要把“当前没发现运行中的 MCP”直接等同于“用户没有配置 MCP”。
- 先检查运行状态；只有未运行时，才进入配置检查。
- 只支持 `Cursor / VS Code` 的配置查找；如果当前宿主无法判断，先询问用户当前使用哪个应用。
- 不要凭推断填充 `project-id`、`access-token`、`apiBaseUrl`。
- 不要直接在终端运行 `npx apifox-mcp-server` 试图临时拉起 MCP；宿主不会接管这个进程。

## 阶段 A：先检查 MCP 是否已运行

1. 使用当前宿主提供的 MCP server 列表、工具列表或搜索能力，查找是否已经存在 `apifox`。
2. 命中 `apifox` MCP 或其工具后，直接进入"阶段 D：通过 MCP 读取接口"。
3. 未命中时，不要立刻判定为“未配置”；进入"阶段 B：按当前宿主检查配置"。

## 阶段 B：按当前宿主检查是否已配置

先判断当前用户正在使用哪个应用；当前只支持 `Cursor` 和 `VS Code`。

如果当前宿主无法可靠判断，先向用户确认：

- 你现在是在 `Cursor` 还是 `VS Code` 里使用这个 skill？

### Cursor

按以下顺序检查：

1. 项目级 MCP：`<project>/.cursor/mcp.json`
2. 个人级 / 全局 MCP：`~/.cursor/mcp.json`

关键细节：

- 两者会合并；如果同名 server 同时存在，项目级优先。
- 检查时关注 `servers.apifox` 是否存在。
- 若存在 `servers.apifox`，继续确认它至少包含可启动服务器所需的关键字段，例如：
    - `command`
    - `args`
    - `APIFOX_ACCESS_TOKEN` 或等价敏感参数来源

### VS Code

按以下顺序检查：

1. 工作区级 MCP：`<project>/.vscode/mcp.json`
2. 用户级 MCP：当前 user profile 中的 `mcp.json`

关键细节：

- 对于用户级配置，优先通过命令面板执行 `MCP: Open User Configuration` 打开，不要硬编码 profile 的磁盘路径。
- 检查时关注 `servers.apifox` 是否存在。
- 若存在 `servers.apifox`，继续确认它至少包含可启动服务器所需的关键字段，例如：
    - `type`（若宿主要求）
    - `command`
    - `args`
    - `APIFOX_ACCESS_TOKEN` 或等价敏感参数来源

## 阶段 C：根据配置检查结果分支

### 情况 1：找到 `apifox` 配置，且关键字段齐全

判定为：**已配置，但当前宿主里没有运行起来**。

此时不要让用户重新配置，应该引导用户在当前宿主里启动或重载 MCP：

- `Cursor`：打开设置中的 MCP 管理界面，找到 `apifox` 并启动；必要时重启 Cursor。
- `VS Code`：命令面板执行 `MCP: List Servers`，找到 `apifox` 并启动；必要时执行 `Developer: Reload Window`。

用户回复“已启动”或“继续”后，再重新执行一次阶段 A。

二次探测规则：

- 二次探测命中 → 进入阶段 D。
- 二次探测仍未命中 → 报告“配置已存在，但 MCP 仍未成功启动”，提示用户检查：
    - 配置 JSON 是否合法
    - token / 项目参数是否有效
    - 宿主里的 MCP 输出日志

### 情况 2：没有找到 `apifox` 配置

判定为：**当前宿主下未配置 Apifox MCP**。

此时不要继续猜测、不要生成占位接口数据，也不要直接进入读取阶段。

正确动作：

1. 明确告诉用户当前未找到 `apifox` MCP 配置。
2. 告诉用户应该去哪里配置：
    - `Cursor`：优先检查或创建 `<project>/.cursor/mcp.json`；也可以在宿主的 MCP 配置界面中完成配置。
    - `VS Code`：优先检查或创建 `<project>/.vscode/mcp.json`；也可以执行 `MCP: Open User Configuration` 或 `MCP: Add Server`。
3. 引导用户从 **Apifox 客户端** 复制官方 MCP 配置片段，再完成配置。
4. 提示用户配置完成后，重新启动 MCP 或重启宿主，再回来重试当前请求。

### 情况 3：找到 `apifox` 配置，但字段明显不完整

判定为：**配置存在，但不可可靠启动**。

此时应明确指出缺失项，不要替用户补真实值。

常见缺失项：

- `command`
- `args`
- `project-id`
- `APIFOX_ACCESS_TOKEN`
- `apiBaseUrl` / `apifox-api-base-url`

处理方式：

1. 告诉用户当前配置不完整。
2. 指出缺失字段。
3. 引导用户从 **Apifox 客户端** 复制官方 MCP 配置片段覆盖或修正。
4. 提示用户修正后重新启动 MCP，再回来重试。

## 配置片段来源

Apifox MCP 的关键参数因人因项目而异，不要硬编码：

- `project-id`：每个 Apifox 项目唯一。
- `access-token`：用户个人令牌，属于敏感凭据。
- `apiBaseUrl`：企业版自建实例地址，不同企业不同。

正确的引导方式：

1. 让用户打开 **Apifox 企业版客户端**。
2. 进入 `MCP Server` / `AI 工具` 等相关入口。
3. 选择当前宿主（`Cursor` 或 `VS Code`）。
4. 复制官方生成的 MCP 配置片段。
5. 完成宿主中的配置后，再回来重试。

## 配置形态参考

下面仅展示 `mcp.json` 的基本形态，真实值以 Apifox 客户端复制的官方片段为准。

```jsonc
{
    "servers": {
        "apifox": {
            "type": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "apifox-mcp-server@latest",
                "--project-id=<从 Apifox 客户端复制>",
                "--apifox-api-base-url=<企业版地址>"
            ],
            "env": {
                "APIFOX_ACCESS_TOKEN": "<你的个人 token>"
            }
        }
    }
}
```

关键细节：

- `Cursor` 和 `VS Code` 都使用 `mcp.json` 形态配置 MCP。
- 如果把敏感值写进被 git 跟踪的项目文件，要先提醒用户检查风险。
- 不要把仓库里的示例值当成真实可用值直接写入。

## 阶段 D：通过 MCP 读取接口

1. 如果可用的 Apifox MCP 工具支持直接读取单接口，将用户给出的 Apifox URL 或接口路径传入工具获取接口详情。
2. 如果 MCP 只返回整个项目的 OAS 文档，从中定位到目标接口的 `path` 和 `method`。
3. 当前常见的 Apifox MCP 可能只暴露项目级 OAS 读取能力，无法仅凭协作链接里的 `api-<id>` 定位单接口；这种情况下必须要求用户补充 `method + path`，或进入替代输入。
4. 提取下一节"必要结构字段"中列出的数据。

### 必要结构字段

在 MCP 返回结果中尽量提取这些字段：

- `name`
- `method`
- `path`
- `request_schema`
- `response_schema`
- `response_example`

可选但有帮助的字段：

- `service_name`
- `tag_name`
- `base_path`
- `description`

### 提取优先级

当同一信息存在多种来源时，按以下顺序使用：

1. 显式响应示例
2. 响应 schema 中内嵌的 example
3. 由 schema 推导出的占位对象

对于请求数据：

1. 显式 request body schema
2. query/path/header 参数定义
3. 空对象

### 链接处理

- 把用户提供的 Apifox URL 视为主定位信息。
- 如果链接里带有项目、目录或接口 ID，只在确实有助于追踪来源时，才在输出总结里保留。
- 不要把项目特定 ID 硬编码进生成文件，除非它确实能帮助人类追踪来源。

### 读取失败的处理

如果 MCP 已运行，但本次读取失败：

- 报告失败原因，例如鉴权、网络、URL 不属于当前 `project-id`。
- 不要继续生成文件。
- 询问用户是否提供替代输入；如愿意，进入阶段 E；否则停止。

## 阶段 E：替代输入（仅在用户明确不走 MCP 或读取失败时）

当 MCP 已运行但读取失败，或用户明确表示这次不继续走 MCP 时，如果用户愿意提供替代数据，按以下步骤处理：

### 接受的替代输入格式

1. **OpenAPI / Swagger 文件**：JSON 或 YAML，可以是文件路径或粘贴内容。
2. **接口 JSON 定义**：直接粘贴的单个接口 JSON。
3. **手动描述**：用户口述或文本描述 `method`、`path`、请求参数、响应结构。

### 处理规则

- 从替代输入中提取与阶段 D 相同的结构化字段。
- 缺少的字段标记为空或未知，不要编造。
- 在最终输出总结中注明数据来源为"替代输入"，并指明具体格式。
- 提取完成后，归一化为 API Interface Artifact；如果用户还需要 TypeScript 或 Mockoon，由外层编排继续调用 `generate-ts-api` 或 `mockoon-route`。

### 用户无法提供替代输入

明确告知 skill 被 Apifox MCP 阻塞，本次终止，不写任何文件。

## 提取接口业务错误码

获取到接口数据后，从「接口说明」（description）字段中逐行匹配 `bizCode_<code>=<msg>`。

- 正则：`/^bizCode_(\d+)\s*=\s*(.+)$/gm`
- 提取到 → 传递给阶段 4 生成 `biz-error.<code>` response
- 未提取到 → 跳过，不编造

### 示例

接口说明原文：

```
bizCode_801=无权访问
bizCode_802=参数错误
```

提取结果：

```json
[
    { "code": 801, "message": "无权访问" },
    { "code": 802, "message": "参数错误" }
]
```
