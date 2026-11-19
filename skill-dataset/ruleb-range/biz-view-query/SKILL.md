---
name: biz-view-query
description: Queries authorized CSB menus, user-accessible views, and paginated view data through biz-view MCP (get_menu_auth_tree_by_module_menu, get_access_view_list, get_view_page_data). Requires biz-view-mcp to be configured with headers.x-auth-token (from business IT, keep secret). Use when the user asks for OMS/SCRM list data, viewDatasourceId, viewId, default view selection, menu-to-view routing, MCP wiring for CSB views, or mentions biz-view-query. Triggers include 查询视图数据、菜单权限树、可访问视图列表、整机订单等业务列表、以及为 MCP 配置 viewDatasourceId/viewId。
version: "1.1.0"
author: zouaizhou
---

# 营销系统视图数据查询（CSB 菜单 → 视图 → 分页数据）

## 首次使用引导（必须先做）

当用户第一次用自然语言提出「查订单/查列表/查视图数据」等需求时，先用 3～6 句话说明本链路在做什么、依赖什么：

1. **权限与身份**：数据来自 CSB 视图体系；**`biz-view-mcp` 必须在 MCP 配置中显式设置 `headers.x-auth-token` 才能完成身份鉴权**（见下文「MCP 前置检查」中的 JSON 示例）。Token 对应哪个账号，**查到的菜单与列表数据就随该账号权限变化**。
2. **三步链路**：先查**有权限的菜单树** → 再按菜单上的 **viewDatasourceId** 查**可访问视图列表** → 最后用 **viewDatasourceId + viewId** 查**分页列表数据**；用户说的业务名称（如「整机内销订单」）通常落在菜单节点的 `menuName` / `pageCode` 上。
3. **默认视图策略**：同一数据源下往往有多个视图；若用户未指定视图名称，**优先取 `isDefault="1"` 的视图**作为 `viewId`。
4. **自然语言条件（用户侧）**：<!-- 开发注释：advConditions 等为 MCP/上游实现细节，对用户透明；引导话术里不要教用户写「高级条件 JSON」。 -->用户**只需要**用自然语言说清楚「查什么、筛什么」，由代理整理为 `get_view_page_data` 的 **`query`** 入参即可；**不要**向用户展示或要求填写 `advConditions` 等字段名。若用户暂时不说筛选条件，可按「不限条件」处理（`query` 不传或为空，由代理与接口约定决定是否拉全列表）。工具在 `query` 非空时会内部完成列配置与条件拼装，对用户一律表述为「系统根据你的话生成查询条件」。

## MCP 前置检查：`biz-view-mcp`

<!-- 开发注释：用户要求在使用 skill 前检查 MCP；仓库内无法代替用户 IDE 运行时状态，因此用「可执行检查步骤」约束代理行为。 -->

本 skill 依赖 Cursor 中已启用且可用的 **`biz-view-mcp`**，并指向 CSB 的 streamable 端点。

<!-- 开发注释：业务网关侧通常要求 HTTP Header 携带 x-auth-token；skill 需明确「必须配置」与保密义务，避免用户误以为仅配 URL 即可匿名访问。 -->

**硬性要求（身份鉴权）**：`biz-view-mcp` **必须**在 MCP 配置中增加请求头 **`x-auth-token`**，用于上游 **身份鉴权**；未配置或配置错误时，易出现空数据、401/403 或业务权限错误。示例如下（`xxxxx` 替换为本人有效 token）：

```json
"headers": {
  "x-auth-token": "xxxxx"
}
```

- **`x-auth-token` 获取方式**：由**负责对应业务的 IT** 按你们单位流程发放或说明获取渠道；**不要**向无关人员索要或使用他人账号 token。
- **保密义务**：`x-auth-token` 属于个人/账号敏感凭证，**须严格保密**，**不得**泄露给其他人、**不得**粘贴到公共群、共享文档或可被他人访问的仓库文件中。

### 期望配置示例

<!-- 开发注释：此处仅列出与本 skill 配套的 MCP Server key 与 streamable 端点；不在文档中把该地址框定为「dev 环境」。 -->

- **Server key**：`biz-view-mcp`
- **URL**：`https://biz-app-dev.gz.cvte.cn/mcp/streamable/csb`

### `mcp.json` 最小示例（streamable HTTP）

<!-- 开发注释：示例 URL 与业务侧约定一致即可；不在本文档中对该主机名做「dev/非 dev」环境定性。 -->

> 说明：Cursor 不同版本对字段名可能演进；若与你本机 UI 生成结构不一致，以 **Cursor Settings → Tools & MCP** 自动生成为准。

```json
{
  "mcpServers": {
    "biz-view-mcp": {
      "url": "https://biz-app-dev.gz.cvte.cn/mcp/streamable/csb",
      "headers": {
        "x-auth-token": "xxxxx"
      }
    }
  }
}
```

<!-- 开发注释：headers 字段名以 Cursor「Tools & MCP」当前版本为准；若 UI 使用 transport/args 等形式传 header，以 Cursor 官方文档与本机自动生成为准，但语义不变：必须带上 x-auth-token。 -->

### 合并策略（避免覆盖用户其它 MCP）

<!-- 开发注释：自动配置的核心风险是覆盖整个 mcpServers；必须采用「读旧合并写新」。 -->

当工作区已存在 `.cursor/mcp.json` 且包含其它服务器：

1. 读取原 JSON。
2. 在 `mcpServers` 对象中**仅新增/更新**键 `biz-view-mcp`。
3. 写回文件时保持 JSON 格式化与键顺序稳定（可用编辑器格式化）。
4. 若原文件不是对象或缺少 `mcpServers`：不要猜测复杂结构，转「手动配置」路径。

### 认证相关（配置必做 + 排障）

<!-- 开发注释：与 sd-mcp-service 向上游透传 token 的实现解耦；本 skill 面向 Cursor 直连 biz-view-mcp 的场景，强调客户端侧 headers 为必选项。 -->

- **配置必做**：`biz-view-mcp` 的 MCP 配置里 **必须**包含 `headers`，且其中带有键 **`x-auth-token`**（完整结构见上文 `mcp.json` 示例），否则无法完成身份鉴权，工具调用易失败或返回与权限不符的数据。
- **token 来源**：`x-auth-token` 须通过 **负责业务的 IT** 获取或按其指引申请；不得使用来源不明的 token。
- **保密**：个人 `x-auth-token` **仅限本人使用**，**禁止泄露给其他人**；排查问题时也不要求用户把完整 token 发到公开场合，可改为「在本地 MCP 配置中更新后重试」或脱敏说明（仅前后几位）。
- **排障**：若工具返回空数据、HTTP 失败或权限错误：优先让用户确认 **MCP `headers.x-auth-token` 是否已配置、是否过期、是否与当前业务环境匹配**。

### 代理必须执行的检查顺序

1. **在 Cursor「Settings → Tools & MCP」**（或等价入口）确认是否存在名为 **`biz-view-mcp`** 的服务器，且状态为已连接/可用。
2. **鉴权头必查**：确认该服务器配置中已包含 **`headers.x-auth-token`**（或当前 Cursor 版本等价能力）；若用户尚未配置，**明确告知必须配置**、token 须向 **负责业务的 IT** 申请，并提醒 **个人 token 不得外泄**。
3. 若 UI 不便直接读取：检查工作区是否存在 **`.cursor/mcp.json`**，以及用户级 **`~/.cursor/mcp.json`** 是否包含 `mcpServers.biz-view-mcp`，并尽量确认其中是否含 **`headers.x-auth-token`**（**不要**在对话中让用户回显完整 token）。
4. **若缺失**：优先尝试在工作区创建/合并 **`.cursor/mcp.json`**（仅追加 `biz-view-mcp` 条目，保留其它服务器配置不被覆盖），且合并写入的示例 **必须**包含 `url` 与 `headers.x-auth-token` 占位（用户自行替换 `xxxxx`）。
5. **若自动写入失败**（权限、合并冲突、用户拒绝写入仓库文件等）：引导用户手动在 Cursor MCP 设置中添加同名服务器、URL，并**务必**补充 `x-auth-token` 请求头，保存后重试工具调用。

## 工具名与参数（与实现对齐）

<!-- 开发注释：以下工具名来自 sd-mcp-service 的 Spring @Tool(name=...)，是模型调用时必须使用的真实名称。 -->

| 目的 | MCP 工具名 | 关键入参 |
|------|------------|----------|
| 查询用户有权限的菜单树 | `get_menu_auth_tree_by_module_menu` | `menuId` 必填；`userId`、`roleIds` 可选 |
| 查询某数据源下可访问视图列表 | `get_access_view_list` | `viewDatasourceId` 必填 |
| 查询视图分页数据 | `get_view_page_data` | `viewDatasourceId`、`viewId`、`isCustomerView` 必填；用户侧筛选用自然语言 **`query`**（可选）；`advConditions` 等仅代理/集成场景使用，对用户透明 |

### 顶层模块 `menuId` 常量

<!-- 开发注释：用户提供的业务常量，作为不同系统菜单树的根节点过滤入口。 -->

- **SCRM 顶层菜单 `menuId`**：`006d9fb61e9f457aa02a68a59b2b1609`
- **OMS 顶层菜单 `menuId`**：`fbb6fd2e13484aebb8559f5e4fbd5eaf`

当用户未说明系统时：**先根据业务关键词判断**（如「订单/OMS」优先 OMS），不确定则**分别拉两份菜单树**或向用户确认系统边界。

## 接口返回字段对照

<!-- 开发注释：字段说明便于从 JSON 中取值而不误用字段名。 -->

### `get_menu_auth_tree_by_module_menu` → `data[]`

- **`menuName`**：展示给用户的主名称
- **`pageCode`**：稳定业务编码（适合写入配置）
- **`pageUrl`**：前端路由线索
- **`viewDatasourceId`**：进入视图体系的入口 ID（可能为空字符串；以实际返回值为准）
- **`isViewConfig`**：是否为视图配置页（常见 `"1"` / `"0"`）

### `get_access_view_list` → `data[]`

- **`id`**：作为 `get_view_page_data.viewId`
- **`codeName`**：视图名称（展示/消歧）
- **`isDefault`**：`"1"` 表示默认视图（本 skill 的默认选择规则）
- **`isCustomerView`**：透传到 `get_view_page_data.isCustomerView`

### `get_view_page_data`：`query` 与用户透明说明

<!-- 开发注释：与 ViewPageDataQueryTool 实现一致，但面向 skill 读者区分「用户话术」与「代理/排障」。 -->

- **对用户**：只沟通 **`query`**（自然语言筛选）。**`advConditions` 对用户透明**，不要在引导、说明或示例里把「高级条件 JSON」当作用户必会项；用户侧话术统一为「用一句话描述你要查的数据范围」。
- **对代理（调用 MCP）**：当 **`query` 非空**时，工具内部会走「高级查询列 → LCDP AI → 生成服务端条件」链路，**同一次调用中不要再传入手写的 `advConditions`**（即使传了也会被工具忽略，易造成困惑）。当 **`query` 为空**且确有程序集成、排障等需要时，才由调用方显式传 `advConditions` 等字段；**普通帮用户查列表的对话场景，默认不传 `advConditions`**，避免把实现细节暴露给用户。

## 标准查询工作流（菜单 → 视图 → 数据）

### Step A：定位菜单节点（拿到 `viewDatasourceId`）

1. 调用 `get_menu_auth_tree_by_module_menu`，传入对应系统顶层 `menuId`。
2. 在返回 JSON 的 `data` 数组中查找目标菜单：
   - 优先匹配用户描述与 **`menuName`**
   - 其次参考 **`pageCode` / `pageUrl`**
3. 选中节点后读取：
   - **`viewDatasourceId`**：后续视图列表与分页查询的核心键
   - **`isViewConfig`**：经验上 **`"1"`** 才更像「已挂视图配置的可查列表页」；若用户目标不明确，优先展示这类节点供选择

若用户目标菜单在树中找不到：**明确告知「当前 token 对应账号在该模块菜单树下不可见」**，不要猜测 ID。

### Step B：列出可访问视图（拿到 `viewId`）

1. 使用 Step A 得到的 **`viewDatasourceId`** 调用 `get_access_view_list`。
2. 在 `data` 数组中选择视图记录：
   - **`id`**：作为 `get_view_page_data` 的 **`viewId`**
   - **`isDefault`**：若用户未指定视图名称，选择 **`isDefault == "1"`** 的那条；若不存在默认标记，则把候选视图 **`codeName` + `id`** 列表交给用户选择
   - **`isCustomerView`**：原样带入分页查询（列表里常见系统视图为 **`"0"`**；以接口返回值为准）

### Step C：查询分页数据

调用 `get_view_page_data`：

- **`viewDatasourceId`**：来自菜单节点（Step A）
- **`viewId`**：来自视图列表选中项的 `id`（Step B）
- **`isCustomerView`**：来自视图列表选中项的 `isCustomerView`（Step B；禁止空字符串）
- **`query`**：<!-- 开发注释：Step C 与用户交互时只收集自然语言，不引导用户理解 advConditions。 -->将用户的筛选说法整理为自然语言 **`query`**（可选；非空会启用内部 AI 条件生成链路）；**不要**要求用户提供或理解 `advConditions`
- **`pageNum` / `pageSize`**：默认合理分页，避免一次拉全表
- **向用户输出查询结果（全量）**：<!-- 开发注释：全量优先；Excel 为体量过大时的交付形态，不得用抽样冒充全量。 -->将 `get_view_page_data` 的**完整原始返回**（通常为整段 JSON 字符串）**原样、不截断、不省略字段**地呈现给用户；若响应体过长，可分块连续输出（多块拼接后仍为全量），**不得**仅输出部分行或自行概括后声称已代表全量。若接口分页导致仅返回当前页数据，应明确说明「当前为第 N 页全量」并给出 `pageNum`/`pageSize` 与总条数线索（若响应含），便于用户决定是否继续翻页。
- **数据量过大时的 Excel 交付**：<!-- 开发注释：在对话中贴全量 JSON 不可行时，用表格文件承载全量行，与「不得抽样冒充全量」一致。 -->当查询结果在对话中难以完整粘贴（行数/字段过多）时，在**已拿到接口完整响应**并解析出列表数据的前提下，可将**全部业务行**（与当前页或当前响应一致，不得擅自抽样）导出为 **Excel**（如 `.xlsx`，或用户接受的可下载表格格式）提供给用户下载或作为附件；**禁止**用「只导前 N 行」冒充全量，除非用户明确只要样本并在说明中写清。若用户仍需要核对原始结构，应说明 Excel 与 JSON 的对应关系，或在其需要时**继续**提供分块全量 JSON。

## 目标菜单/视图不清晰时的交互策略

当用户描述模糊（多匹配、跨菜单同名、只有职能没有页面名）：

1. 先从菜单树中筛出 **Top N（建议 N≤10）** 候选：展示 `menuName`、`pageCode`、`viewDatasourceId`（如有）、`pageUrl`。
2. 若候选菜单已确定但视图多个：展示 `codeName`、`id`、`isDefault`、`isCustomerView`。
3. **明确请用户回复选项编号或复制 `id`**，再继续调用分页接口。

## 「仅要 ID」模式（给 MCP 或其它工具做配置）

当用户声明只需要 **`viewDatasourceId` + 视图 `viewId` 列表**（不做数据查询）：

1. 仍执行 Step A～B（或只到 B）。
2. 输出结构化结果（Markdown 表格即可）：
   - **菜单定位信息**：`menuName`、`pageCode`、`viewDatasourceId`
   - **视图列表**：`codeName`、`viewId`（即 `id`）、`isDefault`、`isCustomerView`
3. **不要编造**未出现在接口响应里的 ID。

## 结果解读与错误处理（最小集合）

- **HTTP 200 且业务 `status == "0"`**：通常可用；`data` 可能是数组或对象，以接口为准。
- **401/403 或业务非 0**：优先提示用户检查 **token/环境/账号权限**；不要反复用相同参数刷屏式重试。
- **大 JSON 与 Step C 的关系**：<!-- 开发注释：与上文 Step C「全量输出」一致；Excel 为全量行的等价交付形态之一。 -->**Step C 场景下**必须先满足「**全量**」：优先**完整原始 JSON**（可分块）；若体量过大，可用上文 **Excel 全量导出** 作为交付方式。若需帮助阅读，可在**全量交付之后**另起小节做字段说明或统计，**禁止**用「仅摘要」替代全量原文或全量表格。
